import streamlit as st

import cv2

from pyzbar.pyzbar import decode

import numpy as np

import json

import os


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(

    page_title="CampusCrave | QR Scanner",

    page_icon="🍴",

    layout="centered"

)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""

<style>

body {

    background-color: #f5f7f2;

}

.main {

    background-color: #f5f7f2;

}


.header {

    background-color: white;

    padding: 18px 25px;

    border-radius: 15px;

    margin-bottom: 30px;

    border: 1px solid #e5e8e2;

}


.logo {

    color: #263c2b;

    font-size: 27px;

    font-weight: bold;

}


.subtitle {

    color: #858980;

    font-size: 12px;

}


.title {

    text-align: center;

    color: #263c2b;

    font-size: 38px;

    font-weight: bold;

    margin-top: 20px;

}


.description {

    text-align: center;

    color: #777;

    font-size: 14px;

    margin-bottom: 30px;

}


.scanner-card {

    background-color: white;

    padding: 20px;

    border-radius: 20px;

    border: 1px solid #e5e8e2;

}


.success-card {

    background-color: #edf5ea;

    padding: 20px;

    border-radius: 15px;

    border: 1px solid #cdddc8;

    margin-top: 20px;

}


.order-card {

    background-color: white;

    padding: 20px;

    border-radius: 15px;

    border: 1px solid #e5e8e2;

    margin-top: 15px;

}


.order-item {

    padding: 10px;

    border-bottom: 1px solid #eeeeee;

}


.status {

    text-align: center;

    color: #4f7950;

    font-size: 13px;

    margin: 15px;

}


.footer {

    text-align: center;

    color: #999;

    font-size: 11px;

    margin-top: 40px;

}

</style>

""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown("""

<div class="header">

    <div class="logo">
        🍴 CampusCrave
    </div>

    <div class="subtitle">
        Smart College Canteen
    </div>

</div>

""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

st.markdown(

    '<div class="title">Scan Pickup QR Code</div>',

    unsafe_allow_html=True

)


st.markdown("""

<div class="description">

Scan the student's CampusCrave QR code
to verify and collect the food order.

</div>

""", unsafe_allow_html=True)


# =========================================================
# CAMERA
# =========================================================

st.markdown(

    '<div class="scanner-card">',

    unsafe_allow_html=True

)


camera_image = st.camera_input(

    "📷 Open Camera and Scan QR"

)


st.markdown(

    '</div>',

    unsafe_allow_html=True

)


# =========================================================
# QR PROCESSING
# =========================================================

if camera_image is not None:


    # Convert camera image to bytes

    image_bytes = camera_image.getvalue()


    # Convert bytes to numpy array

    image_array = np.frombuffer(

        image_bytes,

        np.uint8

    )


    # Convert to OpenCV image

    frame = cv2.imdecode(

        image_array,

        cv2.IMREAD_COLOR

    )


    # =====================================================
    # CHECK IMAGE
    # =====================================================

    if frame is None:

        st.error(

            "Unable to read the camera image."

        )

        st.stop()


    # =====================================================
    # DECODE QR
    # =====================================================

    qr_codes = decode(frame)


    if qr_codes:


        # Use first QR

        qr = qr_codes[0]


        try:

            qr_text = qr.data.decode(
                "utf-8"
            )

        except Exception:

            st.error(
                "Unable to read QR data."
            )

            st.stop()


        # =================================================
        # PARSE QR DATA
        # =================================================

        try:

            qr_data = json.loads(
                qr_text
            )

        except json.JSONDecodeError:

            st.error(

                "❌ Invalid CampusCrave QR code."

            )

            st.info(

                "Please scan the QR code generated "
                "from the CampusCrave order confirmation page."

            )

            st.stop()


        # =================================================
        # CHECK QR TYPE
        # =================================================

        if qr_data.get("type") != "CampusCrave-Pickup":

            st.error(

                "❌ This is not a CampusCrave pickup QR."

            )

            st.stop()


        # =================================================
        # GET DATA
        # =================================================

        order_id = qr_data.get(
            "orderId",
            "Unknown"
        )

        student_id = qr_data.get(
            "studentId",
            "Unknown"
        )

        total = qr_data.get(
            "total",
            0
        )

        payment_method = qr_data.get(
            "paymentMethod",
            "Unknown"
        )

        order_status = qr_data.get(
            "status",
            "Order Placed"
        )


        # =================================================
        # SUCCESS
        # =================================================

        st.markdown(f"""

        <div class="success-card">

            <h3>
                ✅ CampusCrave QR Verified
            </h3>

            <p>
                <b>Order ID:</b>
                {order_id}
            </p>

            <p>
                <b>Student ID:</b>
                {student_id}
            </p>

        </div>

        """, unsafe_allow_html=True)


        # =================================================
        # ORDER INFORMATION
        # =================================================

        st.markdown("""

        <div class="order-card">

            <h3>
                🍛 Order Information
            </h3>

            <hr>

        """, unsafe_allow_html=True)


        st.markdown(
            f"""
            <div class="order-item">
                <b>Order ID:</b> {order_id}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="order-item">
                <b>Student ID:</b> {student_id}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="order-item">
                <b>Total Amount:</b> ₹{total}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="order-item">
                <b>Payment:</b> {payment_method}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="order-item">
                <b>Current Status:</b> {order_status}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


        # =================================================
        # COLLECTION CONFIRMATION
        # =================================================

        st.markdown("---")


        st.subheader(
            "🍴 Food Collection"
        )


        if order_status == "Completed":

            st.success(

                "This order has already been collected."

            )


        else:

            st.info(

                "Verify the student's order before "
                "confirming food collection."

            )


            if st.button(

                "✅ Confirm Food Collection",

                use_container_width=True

            ):


                # =========================================
                # CREATE UPDATED ORDER
                # =========================================

                updated_order = {

                    "type":
                        "CampusCrave-Pickup",

                    "orderId":
                        order_id,

                    "studentId":
                        student_id,

                    "total":
                        total,

                    "paymentMethod":
                        payment_method,

                    "status":
                        "Completed",

                    "collectionConfirmed":
                        True

                }


                # =========================================
                # SAVE COLLECTION DATA
                # =========================================

                os.makedirs(

                    "data",

                    exist_ok=True

                )


                file_path = os.path.join(

                    "data",

                    "completed_orders.json"

                )


                completed_orders = []


                if os.path.exists(
                    file_path
                ):

                    try:

                        with open(
                            file_path,
                            "r",
                            encoding="utf-8"
                        ) as file:

                            completed_orders =json.load(file)

                    except Exception:

                        completed_orders = []


                completed_orders.append(
                    updated_order
                )


                with open(
                    file_path,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(

                        completed_orders,

                        file,

                        indent=4

                    )


                # =========================================
                # SUCCESS
                # =========================================

                st.success(

                    f"✅ Food collection confirmed for "
                    f"Order {order_id}!"

                )


                st.balloons()


    else:

        # =================================================
        # NO QR
        # =================================================

        st.markdown("""

        <div class="status">

            🔍 No QR code detected.

            <br><br>

            Please place the CampusCrave QR code
            clearly inside the camera frame.

        </div>

        """, unsafe_allow_html=True)


# =========================================================
# INSTRUCTIONS
# =========================================================

st.markdown("---")


st.subheader(
    "How to Scan"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown("""

    **01**

    Open the student's order confirmation.

    """)


with col2:

    st.markdown("""

    **02**

    Show the Pickup QR Code.

    """)


with col3:

    st.markdown("""

    **03**

    Scan and confirm collection.

    """)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""

<div class="footer">

CampusCrave © 2026

<br>

Smart College Canteen

</div>

""", unsafe_allow_html=True)