import streamlit as st

from database import add_product, get_all_products
from qr_utils import generate_qr_image


st.title("📦 Register Product")

st.write(
    "Register a new product and generate a signed TraceQR code."
)


# --------------------------------------------------
# Product name
# --------------------------------------------------

product_name = st.text_input(
    "Product Name",
    placeholder="e.g. Kisna Diamond Ring"
)


# --------------------------------------------------
# Register product
# --------------------------------------------------

if st.button("Register Product", type="primary"):

    if not product_name.strip():

        st.warning(
            "Please enter a product name."
        )

    else:

        # Get existing products
        products = get_all_products()

        # Generate next product ID
        next_number = len(products) + 1

        product_id = f"TRQ-{next_number:04d}"

        # Save product
        add_product(
            product_name.strip(),
            product_id
        )

        # Generate QR
        qr_image = generate_qr_image(product_id)

        # Store in session
        st.session_state["qr_image"] = qr_image
        st.session_state["registered_product_id"] = product_id
        st.session_state["registered_product_name"] = product_name.strip()

        st.success(
            f"✅ Product registered successfully! "
            f"Product ID: {product_id}"
        )


# --------------------------------------------------
# Display QR
# --------------------------------------------------

if "qr_image" in st.session_state:

    st.divider()

    st.subheader("🔐 Your TraceQR Code")

    st.write(
        f"**Product:** "
        f"{st.session_state['registered_product_name']}"
    )

    st.write(
        f"**Product ID:** "
        f"{st.session_state['registered_product_id']}"
    )

    # Display QR
    st.image(
        st.session_state["qr_image"],
        width=300
    )

    # Download QR
    st.download_button(
        label="⬇️ Download QR Code",
        data=st.session_state["qr_image"],
        file_name=(
            f"{st.session_state['registered_product_id']}.png"
        ),
        mime="image/png"
    )