import streamlit as st
import utils

def show():
    # ------------------ TITLE ------------------
    st.title(utils.t("🌾 Sell Crop Residue"))
    st.write(utils.t("Add your crop residue items for sale and earn profit instead of burning."))

    # ------------------ SESSION STATE ------------------
    if "items" not in st.session_state:
        st.session_state["items"] = []

    # ------------------ ADD ITEM FORM ------------------
    st.header(utils.t("Add Item for Sale"))

    name = st.text_input(utils.t("Item Name"), placeholder=utils.t("e.g. Rice Straw Bales"))
    crops_list = ["Rice", "Wheat", "Sugarcane", "Maize", "Cotton", "Other"]
    translated_crops = [utils.t(c) for c in crops_list]
    
    crop_idx = st.selectbox(
        utils.t("Crop Type"),
        range(len(crops_list)),
        format_func=lambda x: translated_crops[x]
    )
    selected_crop = crops_list[crop_idx]

    quantity = st.number_input(
        utils.t("Quantity (tonnes)"),
        min_value=0.1,
        value=1.0,
        step=0.5
    )
    price = st.number_input(
        utils.t("Price per tonne (₹)"),
        min_value=100,
        value=2500,
        step=100
    )
    location = st.text_input(utils.t("Location"), placeholder=utils.t("e.g. Karnal, Haryana"))

    if st.button(utils.t("Add Item"), width="stretch"):
        if name and location:
            st.session_state["items"].append({
                "name": name,
                "crop": selected_crop,
                "qty": quantity,
                "price": price,
                "location": location
            })
            st.success(f"{utils.t('Added')}: {name} — {quantity} {utils.t('tonnes at')} ₹{price}/{utils.t('tonne')}")
        else:
            st.error(utils.t("Please fill in item name and location."))

    st.divider()

    # ------------------ LISTED ITEMS ------------------
    st.header(f"{utils.t('Listed Items')} ({len(st.session_state['items'])})")

    if not st.session_state["items"]:
        st.info(utils.t("No items yet. Add one above."))
    else:
        for i, item in enumerate(st.session_state["items"]):
            total = item["qty"] * item["price"]

            st.subheader(item["name"])
            st.write(
                f"{utils.t('Crop')}: {utils.t(item['crop'])} | "
                f"{utils.t('Qty')}: {item['qty']} {utils.t('tonnes')} | "
                f"{utils.t('Price')}: ₹{item['price']:,}/{utils.t('tonne')}"
            )
            st.write(
                f"{utils.t('Total Value')}: **₹{total:,.0f}** | "
                f"{utils.t('Location')}: {item['location']}"
            )

            if st.button(utils.t("Remove"), key=f"rm_{i}"):
                st.session_state["items"].pop(i)
                st.rerun()

            st.divider()

    # ------------------ PROFIT CALCULATOR ------------------
    st.header(utils.t("Profit Calculator"))

    calc_qty = st.number_input(
        utils.t("Quantity (tonnes)"),
        min_value=0.1,
        value=5.0,
        step=0.5,
        key="cq"
    )
    calc_price = st.number_input(
        utils.t("Selling Price (₹/tonne)"),
        min_value=100,
        value=2800,
        step=100,
        key="cp"
    )
    calc_cost = st.number_input(
        utils.t("Processing Cost (₹/tonne)"),
        min_value=0,
        value=800,
        step=100,
        key="cc"
    )

    if st.button(utils.t("Calculate"), width="stretch"):
        revenue = calc_qty * calc_price
        cost = calc_qty * calc_cost
        profit = revenue - cost

        st.write(f"{utils.t('Revenue')}: ₹{revenue:,.0f}")
        st.write(f"{utils.t('Cost')}: ₹{cost:,.0f}")
        st.write(f"**{utils.t('Profit')}: ₹{profit:,.0f}**")

    st.divider()
    st.caption(f"© {utils.t('AGRI-Intellect')}")
