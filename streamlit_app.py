# =============================================================
# Shelf Life Application
# -------------------------------------------------------------
# Description:
    # Shelf Life is an app that enables you to track pantry items, 
    # monitor expiry dates, generate smart grocery lists, 
    # analyze your environmental impact metrics, and interact with
    # an AI-Powered chat-bot to get recipes for you.
# -------------------------------------------------------------
# Modules:
# 1. Configuration & Gemini
# 2. Google Sheets Connector
# 3. Utility Functions
# 4. Login & Sidebar UI
# 5. Tabs for Expiry, Subtraction, Grocery List, Dashboard
# =============================================================

# -------------------------
# 1. Configuration & Gemini
# -------------------------

    # - Sets up page layout and Gemini API connection
    # - ask_gemini(prompt): Sends user prompt to Gemini 2.0 Flash
    # Update Instructions:
    # - Replace API key using os.environ
    # - Update URL/model if switching Gemini versions
    # - Customize prompt structure as needed

import streamlit as st
import requests
import os

# Access the Gemini API Key
GEMINI_API_KEY = os.environ.get("Gemini")

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# -------------------------
# 2. Google Sheets Connector
# -------------------------

    # - Connects to Google Sheets using gspread + service credentials
    # - get_gsheet_df(): Fetches data from "DB" worksheet
    # - reset_all_session(): Clears session state variables
    # Update Instructions:
    # - Change worksheet name or spreadsheet URL in get_gsheet_df()
    # - Ensure new sheet columns are handled in downstream logic

import pandas as pd
import toml
import gspread
from datetime import date, datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import plotly.express as px

# Page config
st.set_page_config(page_title="Shelf Life", layout="wide")

# Determine if chat window should be shown
if "open_chat" in st.query_params or st.session_state.get("show_chat", False):
    st.session_state.show_chat = True

# Initialize session state keys 
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False


# Constants for CO2 emission calculation
CO2_PER_KG = 2.5  

# -------------------------
# 3. Utility Functions
# -------------------------

    # - get_expiring_items(): Finds items nearing expiry
    # - generate_grocery_list(): Suggests restocking needs
    # - sustainability_dashboard(): Computes CO₂ & money metrics
    # - top_items(): Identifies most used/wasted food items
    # Update Instructions:
        # - Adjust filtering time windows (e.g. 30-day usage)
        # - Add new filters (e.g. category, brand)
        # - Update logic to support new sustainability metrics

def get_gsheet_df():
    secret_str = os.environ.get("GSheets")
    if not secret_str:
        st.error("❌ 'GSheets' secret not found in environment.")

    try:
        creds = toml.loads(secret_str)["connections"]["gsheets"]
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
    except Exception as e:
        st.error(f"❌ Failed to load credentials: {e}")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    client = gspread.authorize(
        ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    )
    worksheet = client.open_by_url(creds["spreadsheet"]).worksheet("DB")
    df = pd.DataFrame(worksheet.get_all_records())
    return df, worksheet

def reset_all_session():
    for k in list(st.session_state.keys()):
        if k not in ['logged_in','username']:
            del st.session_state[k]
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# Ensure session state keys
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

def get_expiring_items(df, username, days):
    # Skip if the Expiry_Date column is missing
    if "Expiry_Date" not in df.columns:
        return pd.DataFrame()

    today    = pd.Timestamp.today().normalize()
    deadline = today + timedelta(days=days)

    # If Username exists, filter by it, otherwise use all rows
    if "Username" in df.columns and username is not None:
        user_df = df[df["Username"] == username].copy()
    else:
        user_df = df.copy()

    user_df["Expiry_Date"] = pd.to_datetime(user_df["Expiry_Date"], errors="coerce")
    return user_df[
        (user_df["Expiry_Date"] >= today) &
        (user_df["Expiry_Date"] <= deadline)
    ]

def generate_grocery_list(df, username, days_ahead=7):
    # Return empty list if entry dates are missing
    if "Date_of_Entry" not in df.columns:
        return pd.DataFrame(columns=["Food_Name","Brand","QUnit","Recommended_Quantity"])

    today = pd.Timestamp.today().normalize()
    tmp   = df.copy()
    tmp["Date_of_Entry"] = pd.to_datetime(tmp["Date_of_Entry"], errors="coerce")

    # Filter to last 30 days, and by user if that column exists
    if "Username" in tmp.columns and username is not None:
        recent = tmp[
            (tmp["Username"] == username) &
            (tmp["Date_of_Entry"] >= today - timedelta(days=30))
        ].copy()
    else:
        recent = tmp[tmp["Date_of_Entry"] >= today - timedelta(days=30)].copy()

    if recent.empty:
        return pd.DataFrame(columns=["Food_Name","Brand","QUnit","Recommended_Quantity"])

    recent["Quantity"] = pd.to_numeric(recent["Quantity"], errors="coerce").fillna(0)
    usage = (
        recent
        .groupby(["Food_Name","Brand","QUnit"])["Quantity"]
        .sum()
        .reset_index()
    )
    usage["Daily_Avg"] = usage["Quantity"] / 30
    usage["Recommended_Quantity"] = (usage["Daily_Avg"] * days_ahead).round().astype(int)

    return usage[usage["Recommended_Quantity"] > 0][
        ["Food_Name","Brand","QUnit","Recommended_Quantity"]
    ]

# Sustainability dashboard function
def sustainability_dashboard(df, username):
    # Prep user data
    user_df = df[df["Username"] == username].copy()
    user_df["Remarks"]      = user_df["Remarks"].fillna("").str.lower()
    user_df["Quantity"]     = pd.to_numeric(user_df["Quantity"], errors="coerce").fillna(0)
    user_df["Weight"]       = pd.to_numeric(user_df["Weight"],   errors="coerce").fillna(0)
    user_df["Price"]        = pd.to_numeric(user_df["Price"],    errors="coerce").fillna(0)
    user_df["Expiry_Date"]  = pd.to_datetime(user_df["Expiry_Date"], errors="coerce")
    user_df["Date_of_Entry"]= pd.to_datetime(user_df["Date_of_Entry"], errors="coerce")

    today = pd.Timestamp.today().normalize()

    # Define wasted = trashed + expired
    trashed = user_df[user_df["Remarks"] == "trashed"]
    expired = user_df[user_df["Expiry_Date"] < today]
    wasted  = pd.concat([trashed, expired]).drop_duplicates()

    # Items that were used (not trashed or expired)
    used = user_df.drop(wasted.index, errors="ignore")

    # Compute CO2 & money
    total_waste = (wasted["Quantity"] * wasted["Weight"]).sum()
    total_used  = (used   ["Quantity"] * used   ["Weight"]).sum()
    co2_emitted = (total_waste / 1000) * CO2_PER_KG
    co2_saved   = (total_used  / 1000) * CO2_PER_KG
    money_wasted = (wasted["Price"] * wasted["Quantity"]).sum()
    money_saved  = (used  ["Price"] * used  ["Quantity"]).sum()

    # Build metrics
    metrics = {
        "👤 User":               username,
        "🗃️ Unique Products":    user_df["Food_Name"].nunique(),
        "📅 Last Shopping Date": user_df["Date_of_Entry"]
                                      .max()
                                      .strftime("%B %d, %Y"),  # e.g. May 25, 2025
        "💨 CO₂ Emissions Contribution (kg)":   round(co2_emitted, 2),
        "🌿 CO₂ Saved (kg)":     round(co2_saved,   2),
        "💸 Money Lost ($)":     round(money_wasted,2),
        "💰 Money Saved ($)":    round(money_saved, 2),
    }

    return co2_saved, money_saved, metrics

# Function to select items that are close to expiry
def top_items(df, username, mode="waste"):
    user_df = df[df["Username"] == username].copy()
    user_df["Expiry_Date"] = pd.to_datetime(user_df["Expiry_Date"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    if mode == "waste":
        trashed = user_df[user_df["Remarks"].str.lower()=="trashed"]
        expired = user_df[user_df["Expiry_Date"] < today]
        filtered = pd.concat([trashed, expired]).drop_duplicates()
    else:
        # Used items exclude anything expired or trashed
        trashed = user_df[user_df["Remarks"].str.lower()=="trashed"]
        expired = user_df[user_df["Expiry_Date"] < today]
        filtered = user_df.drop(pd.concat([trashed, expired]).index, errors="ignore")

    top = (
        filtered
        .groupby("Food_Name")["Quantity"]
        .sum()
        .reset_index()
        .sort_values("Quantity", ascending=False)
        .head(5)
    )
    return top


# -------------------------
# 4. Login & Sidebar UI
# -------------------------

    # - Supports demo login with canned usernames/passwords
    # - Renders sidebar with:
        #   - Logo
        #   - Beta Access Title
        #   - Login form
        #   - Chat Assistant (canned queries + free text input)
    # Update Instructions:
        # - Add users by editing `users` and `name_map` dictionaries
        # - Modify layout or emojis in st.markdown() HTML blocks
        # - Add canned buttons in chat section with new keys/prompts

#Username mapping
users = {"snackhoarder": "password", "canofbeans": "password", "hungryhippo": "password"}
name_map = {"snackhoarder": "Maria", "canofbeans": "Juan", "hungryhippo": "Hari"}

# Loggin states
if st.session_state.get("logged_in", False):
    df, worksheet = get_gsheet_df()
    username = st.session_state.username
else:
    df = pd.DataFrame()
    username = None

with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://huggingface.co/spaces/hgopalan/shelf_timer/resolve/main/shelf_timer_logo.png" width="160">
        </div>
        <br>
        """,
        unsafe_allow_html=True
    )
    
    # Centered bold header
    st.markdown(
        """
        <div style="text-align: center; font-size: 18px; font-weight: bold;">
            🛠️ Shelf Timer Beta Access
        </div>
        <br>
        """,
        unsafe_allow_html=True
    )
    
    # Show login instructions only when not logged in
    if not st.session_state.logged_in:
        st.markdown(
            """
            🔍 Choose from one of the usernames below:  
            `snackhoarder`, `canofbeans`, `hungryhippo`  
            
            🔑 The password is `'password'`
            """
        )
        
    if not st.session_state.logged_in:
        with st.form("login_form", clear_on_submit=False):
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login")
            if submitted:
                if users.get(u) == p:
                    st.session_state.logged_in = True
                    st.session_state.username  = u
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password")
    else:
        st.markdown(f"### 👋 {name_map.get(st.session_state.username)}")

        if st.button("🚪 Logout"):
            reset_all_session()

    # Toggle Chat Assistant
    if st.button("💬 Ask SHELI"):
        st.session_state.show_chat = not st.session_state.show_chat

    # Show Assistant only if toggled on
    if st.session_state.get("show_chat", False):
        st.markdown("## 💬 SHELI")
    
        # Create side-by-side canned response buttons
        canned_col1, canned_col2 = st.columns(2)
    
        if canned_col1.button("🍲 Suggest a Recipe", key="btn_suggest"):
            today = pd.Timestamp.today().normalize()
            unexpired_df = df[
                (df["Username"] == st.session_state.username) &
                (pd.to_datetime(df["Expiry_Date"], errors="coerce") >= today)
            ]
            pantry_items = unexpired_df.apply(
                lambda row: f"{row['Food_Name']} (expires {row['Expiry_Date']})",
                axis=1
            ).dropna().tolist()
            pantry_str = ", ".join(pantry_items)
    
            # Get the user's display name
            user_display_name = name_map.get(st.session_state.username, st.session_state.username)
    
            # Build prompt and send to Gemini
            prompt = (
                f"You are a pantry assistant helping {user_display_name}. "
                f"The user has these unexpired items: {pantry_str}.\n"
                f"Can you suggest a recipe with items that are about to expire or unexpired?"
            )
            with st.spinner("Cooking up some delicious options for you..."):
                response = ask_gemini(prompt)
                if response:
                    st.session_state.last_response = response
    
        if canned_col2.button("🥫 Give me Recipe Ideas?", key="btn_make"):
            today = pd.Timestamp.today().normalize()
            unexpired_df = df[
                (df["Username"] == st.session_state.username) &
                (pd.to_datetime(df["Expiry_Date"], errors="coerce") >= today)
            ]
            pantry_items = unexpired_df.apply(
                lambda row: f"{row['Food_Name']} (expires {row['Expiry_Date']})",
                axis=1
            ).dropna().tolist()
            pantry_str = ", ".join(pantry_items)
    
            # Get the user's display name
            user_display_name = name_map.get(st.session_state.username, st.session_state.username)
    
            # Build prompt and send to Gemini
            prompt = (
                f"You are a pantry assistant helping {user_display_name}. "
                f"The user has these unexpired items: {pantry_str}.\n"
                f"Give me recipe ideas that I can prepare based on these items."
            )
            with st.spinner("Cooking up some delicious options for you..."):
                response = ask_gemini(prompt)
                if response:
                    st.session_state.last_response = response
    
        # Free-form chat input
        with st.form("chat_form", clear_on_submit=False):
            user_query = st.text_input(
                "Ask SHELI...",
                value=st.session_state.get("chat_input", ""),
                key="chat_input_sidebar"
            )
            submitted = st.form_submit_button("Send")
    
            if submitted and user_query:
                today = pd.Timestamp.today().normalize()
                unexpired_df = df[
                    (df["Username"] == st.session_state.username) &
                    (pd.to_datetime(df["Expiry_Date"], errors="coerce") >= today)
                ]
                pantry_items = unexpired_df.apply(
                    lambda row: f"{row['Food_Name']} (expires {row['Expiry_Date']})",
                    axis=1
                ).dropna().tolist()
                pantry_str = ", ".join(pantry_items)
    
                # Get the user's display name
                user_display_name = name_map.get(st.session_state.username, st.session_state.username)
    
                # Build prompt with personalized greeting
                prompt = (
                    f"You are a pantry assistant helping {user_display_name}. "
                    f"The user has these unexpired items: {pantry_str}.\n"
                    f"User question: {user_query}\n"
                    "Respond in a helpful, friendly way."
                )
                with st.spinner("Cooking up some delicious options for you..."):
                    response = ask_gemini(prompt)
                    if response:
                        st.session_state.last_response = response
    
        if st.session_state.get("last_response"):
            st.markdown("**SHELI's thoughts:**")
            st.write(st.session_state.last_response)


# Track chat visibility
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

# -------------------------
# 5. Tabs for Expiry, Subtraction, Grocery List, Dashboard
# -------------------------

    # 📅 Expiry Alerts:
        # - Slider to select days-ahead
        # - Displays items nearing expiry using get_expiring_items()
    # ➖ Subtract Quantity:
        # - Multi-entry item quantity subtraction with trash checkbox
        # - Updates only local session copy (not Google Sheet)
    # 🛒 Grocery List:
        # - Uses 30-day usage to recommend quantities for next X days
        # - Pre-fills item info and lets user confirm purchases
        # - Saves selected items to Google Sheet
    # 📊 Dashboard:
        # - Displays CO₂ impact, savings, item waste vs usage
        # - Renders charts: pie, bar, and line using plotly
    # Update Instructions:
        # - Change thresholds in level_msg() for sustainability levels
        # - Modify visualizations or add new KPIs
        # - Adjust time filters and logic in usage trend calculations

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Shelf Life Timer",
    "➖ Quantities",
    "🛒 Smart Grocery List",
    "📊 Dashboard"
])

# --- Expiry Alerts ---
with tab1:
    st.subheader("📅 Shelf Life Timer")

    if not username:
        st.info("Log in to view expiry alerts.")
    else:
        # Single slider, step = 1 day, shows “X days” in thumb
        days = st.slider(
            "Items expiring within the next:",
            min_value=1,
            max_value=30,
            value=7,
            step=1,
            format="%d day/s",
            key="expiry_days"
        )

        # Fetch and display
        exp_df = get_expiring_items(df, username, days)
        if exp_df.empty:
            st.info("🎉 No items expiring soon!")
        else:
            display_df = exp_df[["Food_Name", "Brand", "Expiry_Date", "Quantity", "QUnit"]].copy()
            display_df.columns = ["Food Name", "Brand", "Expiry Date", "Quantity", "Unit"]
            display_df["Expiry Date"] = pd.to_datetime(display_df["Expiry Date"]).dt.date
            st.dataframe(display_df)
# --- Subtract Quantity ---
with tab2:
    st.subheader("➖ Subtract Quantity")

    if not username:
        st.info("Log in to update inventory.")
    else:
        editable = df[df["Username"] == username].copy()

        # --- Multi‐row support ---
        if "sub_qty_entries" not in st.session_state:
            st.session_state.sub_qty_entries = [0]

        if st.button("➕ Add Another Item"):
            st.session_state.sub_qty_entries.append(len(st.session_state.sub_qty_entries))
        
        # Loop over each subtraction entry
        for idx in st.session_state.sub_qty_entries:
            st.markdown(f"### Subtraction #{idx+1}")

            # 1) Choose food
            food_names = editable["Food_Name"].dropna().unique().tolist()
            food_sel = st.selectbox(
                "Select Food Item",
                options=food_names,
                key=f"food_{idx}"
            )

            if food_sel:
                # 2) Choose brand
                rows = editable[editable["Food_Name"] == food_sel]
                brands = rows["Brand"].dropna().unique().tolist()
                brand_sel = st.selectbox(
                    "Select Brand",
                    options=brands,
                    key=f"brand_{idx}"
                )

                # 3) Compute availability
                sel = rows[rows["Brand"] == brand_sel]
                avail_qty = sel["Quantity"].sum()
                avail_uom = sel["QUnit"].mode().iloc[0] if not sel["QUnit"].mode().empty else "unit"

                # 4) Number input with availability in label
                subq = st.number_input(
                    f"Qty to subtract (Available: {avail_qty:.2f} {avail_uom})",
                    min_value=0.0,
                    max_value=float(avail_qty),
                    value=float(avail_qty),
                    step=0.1,
                    key=f"subq_{idx}"
                )

                # 5) Trash checkbox
                trashed = st.checkbox("🗑️ Mark as Trashed?", key=f"trash_{idx}")

                # 6) Apply
                if st.button(f"✅ Update Inventory #{idx+1}", key=f"upd_{idx}"):
                    row_idx = sel.index[0]
                    df.at[row_idx, "Quantity"] = max(0, df.at[row_idx, "Quantity"] - subq)
                    df.at[row_idx, "Remarks"]  = "trashed" if trashed else df.at[row_idx, "Remarks"]
                    st.success(f"✅ Subtraction #{idx+1} applied!")

# --- Grocery List ---
with tab3:
    st.subheader("🛒 Smart Grocery List")

    if not username:
        st.info("Log in to generate grocery list.")
    else:
        # Single slider for days
        days = st.slider(
            "I need food for the next:",
            min_value=1,
            max_value=30,
            value=7,
            step=1,
            format="%d day/s",
            key="grocery_days"
        )

        # Generate list
        gl_df = generate_grocery_list(df, username, days)
        if gl_df.empty:
            st.info("✅ No grocery needs right now.")
        else:
            gl_df['Recommended_Quantity'] = gl_df['Recommended_Quantity'].astype(int)

            # Quick stats
            colA, colB = st.columns(2)
            colA.metric("🛒 Total Items", len(gl_df))
            colB.metric("📦 Food Types", gl_df['Food_Name'].nunique())

            # Food types breakdown (from original df)
            type_df = df[df['Username'] == username][['Food_Name','Brand','Food_Type']].drop_duplicates()
            breakdown = gl_df.merge(type_df, on=['Food_Name','Brand'], how='left')
            counts_df = breakdown['Food_Type'].value_counts().reset_index(name='Count').rename(columns={'index':'Food_Type'})
            if not counts_df.empty and 'Food_Type' in counts_df.columns:
                fig = px.pie(
                    counts_df,
                    names='Food_Type',
                    values='Count',
                    title='Food Types Breakdown',
                    hole=0.3
                )
                fig.update_traces(textinfo='percent+label', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No food type data available.")

            # Display table
            st.dataframe(
                gl_df[['Food_Name', 'Brand', 'Recommended_Quantity', 'QUnit']],
                use_container_width=True
            )

            # Shopping checklist
            shop_date = st.date_input("🗓️ Shopping date:", value=date.today(), key="shop_date")
            exp_default = shop_date + timedelta(days=7)
        
            # 7) Shopping checklist (one row per item)
            st.markdown("### 📝 Shopping Checklist")
            entries = []
            for idx, row in gl_df.iterrows():
                # look up pre-fills
                orig = df[
                    (df["Username"] == username) &
                    (df["Brand"]    == row["Brand"])    &
                    (df["Food_Name"]== row["Food_Name"])
                ]
                o = orig.iloc[0] if not orig.empty else {}
                ft_prefill = o.get("Food_Type", "")
                wt_prefill = float(o.get("Weight", 0.0))
                wu_prefill = o.get("WUnit", "")
                pr_prefill = float(o.get("Price", 0.0))
        
                qty    = int(row["Recommended_Quantity"])
                tot_w  = wt_prefill * qty
                tot_p  = pr_prefill * qty
        
                cols = st.columns([.5,1,1,1,1,1,1,1,1,1,1,1])
                chk = cols[0].checkbox("", key=f"chk_{idx}")
                cols[1].text_input("", value=ft_prefill, key=f"ft_{idx}")
                cols[2].text_input("", value=row["Brand"], key=f"bd_{idx}")
                cols[3].text_input("", value=row["Food_Name"], key=f"fn_{idx}")
                cols[4].number_input("", value=qty, min_value=0, step=1, key=f"qty_{idx}")
                cols[5].text_input("", value=row["QUnit"], key=f"qu_{idx}")
                cols[6].number_input("", value=wt_prefill, min_value=0.0, step=0.1, key=f"wt_{idx}")
                cols[7].text_input("", value=wu_prefill, key=f"wu_{idx}")
                cols[8].text_input("", value=f"{tot_w:.2f}", disabled=True, key=f"tqw_{idx}")
                cols[9].number_input("", value=pr_prefill, min_value=0.0, step=0.01, key=f"pr_{idx}")
                cols[10].text_input("", value=f"{tot_p:.2f}", disabled=True, key=f"tpr_{idx}")
                # Expiry displayed as text
                cols[11].text_input("", value=exp_default.strftime("%Y-%m-%d"), disabled=True, key=f"exp_{idx}")
        
                # store
                entries.append((chk, ft_prefill, row["Brand"], row["Food_Name"],
                                qty, row["QUnit"], wt_prefill, wu_prefill,
                                tot_w, pr_prefill, tot_p, exp_default))
        
            # 8) Save button
            if st.button("Items Purchased"):
                df_sheet, worksheet = get_gsheet_df()
                saved = 0
                for (chk, ft, bd, fn, qty, qu, wt, wu, tqw, pr, tpr, expd) in entries:
                    if chk:
                        worksheet.append_row([
                            username,
                            shop_date.strftime("%Y-%m-%d"),  # Date_of_Entry
                            shop_date.strftime("%Y-%m-%d"),  # Date_of_Purchase
                            ft,  bd, fn, qty, qu, wt, wu, tqw, pr, tpr, expd.strftime("%Y-%m-%d")
                        ])
                        saved += 1
                st.success(f"✅ {saved} purchased item(s) saved!")


# --- Dashboard ---
with tab4:
    st.subheader("📊 Sustainability & Savings Dashboard")

    if not username:
        st.info("Log in to view dashboard.")
    else:
        # Compute base metrics
        co2_saved, money_saved, base_metrics = sustainability_dashboard(df, username)

        # Prepare DF once
        user_df = df[df["Username"] == username].copy()
        user_df["Expiry_Date"] = pd.to_datetime(user_df["Expiry_Date"], errors="coerce")
        today = pd.Timestamp.today().normalize()

        # Counts
        expired_count = int((user_df["Expiry_Date"] < today).sum())
        soon_count    = int(((user_df["Expiry_Date"] >= today) &
                             (user_df["Expiry_Date"] <= today + timedelta(days=5))).sum())

        # Assemble metrics (date already pretty-printed by sustainability_dashboard)
        metrics = {
            "👤 User":               base_metrics["👤 User"],
            "🗃️ Unique Products":    base_metrics["🗃️ Unique Products"],
            "📅 Last Shopping Date": base_metrics["📅 Last Shopping Date"],
            "❌ Expired Items":            expired_count,
            "⏳ Items Expiring Soon":      soon_count,
            "💨 CO₂ Emissions Contribution (kg)":  base_metrics["💨 CO₂ Emissions Contribution (kg)"],
            "🌿 CO₂ Saved (kg)":     base_metrics["🌿 CO₂ Saved (kg)"],
            "💸 Money Lost ($)":     base_metrics["💸 Money Lost ($)"],
            "💰 Money Saved ($)":    base_metrics["💰 Money Saved ($)"],
        }

        # Display in two rows of four metrics
        rows = [list(metrics.items())[i:i+4] for i in range(0, len(metrics), 4)]
        for row in rows:
            cols = st.columns(4)
            for col, (label, value) in zip(cols, row):
                col.metric(label, value)

        # Sustainability Level
        def level_msg(c, m):
            if c > 200 and m > 400:
                return "🏆 Level 4: Sustainability Champion!"
            if c > 100 and m > 200:
                return "🥇 Level 3: Outstanding savings!"
            if c > 50 and m > 100:
                return "🎖️ Level 2: Great impact!"
            if c > 10 and m > 20:
                return "🔰 Level 1: Good start!"
            return "🚀 Getting Started"

        st.success(level_msg(co2_saved, money_saved))

        # Top Items Breakdown
        st.markdown("---\n### 🍽️ Top Item Breakdown")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🗑️ Top Wasted Items")
            wdf = top_items(df, username, mode="waste")
            if not wdf.empty:
                st.dataframe(wdf)
                fig = px.pie(
                    wdf,
                    names='Food_Name',
                    values='Quantity',
                    title='Top Wasted Items',
                    hole=0.3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No wasted items.")

        with col2:
            st.markdown("#### ✅ Top Used Items")
            udf = top_items(df, username, mode="used")
            if not udf.empty:
                st.dataframe(udf)
                fig = px.pie(
                    udf,
                    names='Food_Name',
                    values='Quantity',
                    title='Top Used Items',
                    hole=0.3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No used items.")

        # Expiration Breakdown by Food Type
        st.markdown("---\n### 🏷️ Expiration Breakdown by Food Type")
        exp_items = user_df[user_df["Expiry_Date"] < today]
        soon      = user_df[
            (user_df["Expiry_Date"] >= today) &
            (user_df["Expiry_Date"] <= today + timedelta(days=7))
        ]
        exp_col = pd.concat([exp_items, soon])
        if not exp_col.empty and "Food_Type" in exp_col.columns:
            counts_df = (
                exp_col["Food_Type"]
                .value_counts()
                .reset_index(name="Count")
                .rename(columns={"index": "Food_Type"})
            )
            fig = px.pie(
                counts_df,
                names='Food_Type',
                values='Count',
                title='Expiration Breakdown by Food Type',
                hole=0.3
            )
            fig.update_traces(textinfo='percent+label', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expiration breakdown available.")

        # Usage Trend Over Time
        st.markdown("---\n### 📈 Usage Trend Over Time")
        col_start, col_end = st.columns(2)
        start = col_start.date_input("Start Date", datetime.today() - timedelta(days=30), key="usage_start")
        end   = col_end.date_input("End Date",   datetime.today(),                  key="usage_end")
        
        # Convert to datetime once
        user_df['Date_of_Entry'] = pd.to_datetime(user_df['Date_of_Entry'], errors='coerce')
        
        mask = (
            (user_df['Date_of_Entry'] >= pd.to_datetime(start)) &
            (user_df['Date_of_Entry'] <= pd.to_datetime(end))
        )
        usage_df = user_df[mask].copy()
        
        if not usage_df.empty:
            usage = (
                usage_df
                .groupby('Date_of_Entry')['Quantity']
                .sum()
                .reset_index()
            )
            fig = px.line(
                usage,
                x='Date_of_Entry',
                y='Quantity',
                markers=True,
                title='Quantity Used Over Time'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No usage data in this range.")

        # Sustainability Impact by Food Item
        st.markdown("---\n### 🌍 Sustainability Impact by Food Item")
        impact = (
            user_df
            .assign(CO2_Emitted=lambda x: (x['Weight'] * x['Quantity'] / 1000) * CO2_PER_KG)
            .groupby('Food_Name')['CO2_Emitted']
            .sum()
            .reset_index()
            .sort_values(by='CO2_Emitted', ascending=False)
            .head(10)
        )
        if not impact.empty:
            fig = px.bar(
                impact,
                x='CO2_Emitted',
                y='Food_Name',
                orientation='h',
                title='Top CO₂-Intensive Items',
                labels={'CO2_Emitted': 'CO₂ Emitted (kg)', 'Food_Name': ''}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for impact chart.")