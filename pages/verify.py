import streamlit as st
from user_agents import parse
from streamlit_geolocation import streamlit_geolocation

from database import (
    get_all_products,
    get_product,
    add_scan,
    get_scans_for_product
)

from qr_utils import verify_signature


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="TraceQR Verification",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ==================================================
# HIDE SIDEBAR / ADMIN NAVIGATION
# ==================================================

st.markdown(
    """
    <style>

    [data-testid="stSidebarNav"] {
        display: none;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# AUTOMATIC DEVICE DETECTION
# ==================================================

ua_string = st.context.headers.get("User-Agent", "")

ua = parse(ua_string)

device_label = f"{ua.device.family} ({ua.os.family})"


# ==================================================
# PAGE HEADER
# ==================================================

st.title("🔐 TraceQR")

st.subheader("Product Verification")

st.write(
    "Scan verification powered by TraceQR."
)


# ==================================================
# READ QR QUERY PARAMETERS
# ==================================================

params = st.query_params

qr_product_id = params.get("id", None)
qr_signature = params.get("sig", None)


# ==================================================
# CASE 1 — REAL QR VERIFICATION
# ==================================================

if qr_product_id and qr_signature:

    product_id = qr_product_id

    # --------------------------------------------------
    # Verify HMAC signature
    # --------------------------------------------------

    signature_valid = verify_signature(
        qr_product_id,
        qr_signature
    )

    # ==================================================
    # INVALID SIGNATURE
    # ==================================================

    if not signature_valid:

        st.error(
            "❌ INVALID PRODUCT"
        )

        st.warning(
            "The QR code could not be authenticated. "
            "It may have been modified, copied incorrectly, "
            "or may not be a genuine TraceQR code."
        )

        st.stop()

    # ==================================================
    # FIND PRODUCT
    # ==================================================

    product = get_product(qr_product_id)

    if not product:

        st.error(
            "❌ PRODUCT NOT FOUND"
        )

        st.warning(
            "This product does not exist in the TraceQR "
            "verification database."
        )

        st.stop()

    # ==================================================
    # VALID PRODUCT
    # ==================================================

    st.success(
        "✓ QR CODE AUTHENTICATED"
    )

    st.divider()

    st.subheader(
        "🟢 Genuine Product"
    )

    st.write(
        f"**Product:** {product.name}"
    )

    st.write(
        f"**Product ID:** {product.product_id}"
    )

    st.success(
        "This QR code is authentic and the product "
        "is registered with TraceQR."
    )

    # --------------------------------------------------
    # Device information
    # --------------------------------------------------

    st.divider()

    st.write(
        f"📱 **Device detected:** {device_label}"
    )

    # --------------------------------------------------
    # Location
    #
    # Currently manual because browser GPS requires
    # HTTPS + user permission.
    #
    # This will be replaced with automatic geolocation
    # after deployment.
    # --------------------------------------------------

    location = st.selectbox(
        "📍 Verification Location",
        [
            "Mumbai",
            "Delhi",
            "Bangalore",
            "Hyderabad",
            "Dubai",
            "London"
        ]
    )

    # ==================================================
    # RECORD SCAN AUTOMATICALLY
    # ==================================================

    scan_key = (
        f"{product_id}_"
        f"{qr_signature}_"
        f"{location}"
    )

    if (
        "recorded_scans"
        not in st.session_state
    ):
        st.session_state.recorded_scans = set()

    # --------------------------------------------------
    # Prevent Streamlit reruns from creating duplicate
    # scans during the same verification session.
    # --------------------------------------------------

    if scan_key not in st.session_state.recorded_scans:

        add_scan(
            product_id=product_id,
            location=location,
            device=device_label
        )

        st.session_state.recorded_scans.add(
            scan_key
        )

        scan_recorded = True

    else:

        scan_recorded = False

    # ==================================================
    # VERIFICATION RESULT
    # ==================================================

    st.divider()

    st.success(
        "✅ Verification Successful"
    )

    st.write(
        "The product's QR signature is valid and "
        "matches a registered TraceQR product."
    )

    if scan_recorded:

        st.caption(
            "Verification scan recorded."
        )

    else:

        st.caption(
            "This verification has already been recorded "
            "during this session."
        )


# ==================================================
# CASE 2 — MANUAL TESTING
# ==================================================

else:

    st.info(
        "No QR code was detected. "
        "Manual verification mode is available for testing."
    )

    # --------------------------------------------------
    # Get registered products
    # --------------------------------------------------

    products = get_all_products()

    if not products:

        st.warning(
            "No products have been registered yet."
        )

        st.stop()

    # --------------------------------------------------
    # Product dropdown
    # --------------------------------------------------

    product_options = {
        f"{product.product_id} — {product.name}":
        product.product_id
        for product in products
    }

    selected_product = st.selectbox(
        "Select Product",
        list(product_options.keys())
    )

    product_id = product_options[
        selected_product
    ]

    product = get_product(product_id)

    # --------------------------------------------------
    # Product information
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "Product Information"
    )

    st.write(
        f"**Product:** {product.name}"
    )

    st.write(
        f"**Product ID:** {product.product_id}"
    )

    # --------------------------------------------------
    # Automatically detected device
    # --------------------------------------------------

    st.write(
        f"📱 **Device detected:** {device_label}"
    )

    # --------------------------------------------------
    # Manual location for testing
    # --------------------------------------------------

    location = st.selectbox(
        "📍 Verification Location",
        [
            "Mumbai",
            "Delhi",
            "Bangalore",
            "Hyderabad",
            "Dubai",
            "London"
        ]
    )

    # --------------------------------------------------
    # Manual verification button
    # --------------------------------------------------

    if st.button(
        "✅ Verify Product",
        type="primary"
    ):

        st.divider()

        st.success(
            "🟢 Genuine Product"
        )

        st.write(
            "This product is registered in the "
            "TraceQR database."
        )

        # --------------------------------------------------
        # Record manual test scan
        # --------------------------------------------------

        add_scan(
            product_id=product_id,
            location=location,
            device=device_label
        )

        st.caption(
            "Test verification scan recorded."
        )


# ==================================================
# NOTE FOR FUTURE DAY 2
# ==================================================

# Risk scoring will be added later.
#
# After the risk engine is implemented:
#
# Low risk:
#     🟢 Genuine
#
# Suspicious:
#     🟡 Verification requires attention
#
# High risk:
#     🔴 Potential counterfeit / cloned QR
#
# The customer-facing page will then show the
# appropriate result based on the product's
# scan history.