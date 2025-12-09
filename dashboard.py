import streamlit as st
import os
import pandas as pd
from scout import Scout
from studio import Studio
from publisher import Publisher
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# --- CONFIGURATION & SETUP ---
st.set_page_config(page_title="Racing Tamizhan Console", page_icon="🏎️", layout="wide")

# --- AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == os.getenv("ADMIN_PASSWORD", "admin"): # Default fallback
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # Stop execution if not authenticated

st.title("🏎️ Racing Tamizhan Auto System")

# --- SESSION STATE INITIALIZATION ---
if 'scout' not in st.session_state:
    st.session_state.scout = Scout()
if 'studio' not in st.session_state:
    st.session_state.studio = Studio()
if 'publisher' not in st.session_state:
    st.session_state.publisher = Publisher()

if 'news_items' not in st.session_state:
    st.session_state.news_items = []
if 'generated_assets' not in st.session_state:
    st.session_state.generated_assets = []
if 'approved_assets' not in st.session_state:
    st.session_state.approved_assets = []

# --- SIDEBAR: Status & Config ---
with st.sidebar:
    if os.path.exists("assets/branding/logo.png"):
        st.image("assets/branding/logo.png", use_container_width=True)
    else:
        st.title("🏎️")
    st.header("System Status")
    
    # Metrics
    m1, m2 = st.columns(2)
    m1.metric("News Items", len(st.session_state.news_items))
    m2.metric("Assets Ready", len(st.session_state.generated_assets))
    
    st.divider()
    st.write(" **Configuration**")
    if os.getenv("IG_USERNAME"):
        st.success(f"Instagram: {os.getenv('IG_USERNAME')}")
    else:
        st.error("Instagram: Not Configured")
        
    st.divider()
    if st.button("Reset Session", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Tabs - Use icons for better visual
tab1, tab2, tab3 = st.tabs(["🌎 Scout (News)", "🎨 Studio (Create)", "🚀 Publisher (Upload)"])

# --- TAB 1: SCOUT ---
with tab1:
    st.subheader("Latest Motorsport News")
    
    col_act, col_info = st.columns([1, 4])
    with col_act:
        if st.button("🔄 Fetch News", type="primary", use_container_width=True):
            with st.status("Scouting channels...", expanded=True) as status:
                st.write("Connecting to RSS feeds...")
                st.session_state.news_items = st.session_state.scout.fetch_news()
                status.update(label="Scouting Complete!", state="complete", expanded=False)
            st.rerun()
            
    if st.session_state.news_items:
        # Display as a clean grid
        for item in st.session_state.news_items:
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                with c1:
                    if item['image_url']:
                        st.image(item['image_url'], use_container_width=True)
                    else:
                        st.color_picker("", "#CCCCCC", disabled=True)
                with c2:
                    st.markdown(f"### {item['headline_en']}")
                    st.caption(f"{item.get('type', 'NEWS')} • {item['source']} • {item['id']}")
                    with st.expander("Read Summary"):
                        st.write(item.get('summary', 'No summary available.'))

# --- TAB 2: STUDIO ---
with tab2:
    st.subheader("Creative Studio")
    
    if not st.session_state.news_items:
        st.info("👋 Go to the **Scout** tab to fetch news first.")
    else:
        # Toolbar
        c_tool1, c_tool2, c_tool3 = st.columns([1, 1, 2])
        if c_tool1.button("Select All"):
            for i in range(len(st.session_state.news_items)): st.session_state[f"select_{i}"] = True
            st.rerun()
        if c_tool2.button("Deselect All"):
            for i in range(len(st.session_state.news_items)): st.session_state[f"select_{i}"] = False
            st.rerun()

        # Selection Grid
        st.write("Select stories to generate content for:")
        selected_indices = []
        
        # Grid layout for selection (2 columns)
        for i in range(0, len(st.session_state.news_items), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(st.session_state.news_items):
                    item = st.session_state.news_items[i+j]
                    with cols[j]:
                        key = f"select_{i+j}"
                        if key not in st.session_state: st.session_state[key] = True
                        if st.checkbox(f"{item['headline_en']}", key=key):
                            selected_indices.append(i+j)
        
        st.divider()
        st.subheader("Generation Actions")
        
        g1, g2 = st.columns(2)
        
        with g1:
            if st.button("🖼️ Generate Images", type="primary", use_container_width=True):
                st.session_state.generated_assets = [] # Reset
                selected_items = [st.session_state.news_items[i] for i in selected_indices]
                
                progress_text = "Starting creative process..."
                my_bar = st.progress(0, text=progress_text)
                
                for idx, item in enumerate(selected_items):
                    my_bar.progress((idx) / len(selected_items), text=f"Design: {item['headline_en']}")
                    image_path = st.session_state.studio.generate_image(item)
                    if image_path:
                         st.session_state.generated_assets.append({
                             "type": "image",
                             "path": image_path,
                             "data": item,
                             "approved": False
                         })
                my_bar.empty()
                st.success(f"✨ Created {len(st.session_state.generated_assets)} designs.")
                
        with g2:
             if st.button("🎥 Generate Reel / Short", type="primary", use_container_width=True):
                 if not selected_indices:
                     st.error("Select items above.")
                 else:
                     selected_items_for_video = [st.session_state.news_items[i] for i in selected_indices]
                     with st.status("🎬 Producing Video Digest...", expanded=True) as status:
                         st.write("Generating AI Voiceovers...")
                         # logic tied to studio gen
                         st.write("Compositing video & effects...")
                         video_path = st.session_state.studio.generate_video(selected_items_for_video)
                         status.update(label="Production Complete!", state="complete", expanded=False)
                     
                     if video_path:
                         st.success("✅ Video Ready!")
                         st.video(video_path)
                         st.session_state.generated_assets.append({
                             "type": "video",
                             "path": video_path,
                             "data": {"headline_en": f"News Digest {len(selected_items_for_video)} Stories", "type": "REEL"},
                             "approved": False,
                             "caption": "⚡ Fast F1 News Digest! \n\nCheck out the top stories of the day! \n\n#F1 #RacingTamizhan #Shorts #Reels"
                         })
            
    # Review Section
    if st.session_state.generated_assets:
        st.divider()
        st.subheader("Review & Approve")
        
        for i, asset in enumerate(st.session_state.generated_assets):
            with st.container(border=True):
                col1, col2 = st.columns([1, 1])
                with col1:
                    # Display based on type
                    if asset['type'] == 'video':
                        st.video(asset['path'])
                        st.caption(os.path.basename(asset['path']))
                    else:
                        st.image(asset['path'], caption=os.path.basename(asset['path']))
                    
                with col2:
                    st.markdown(f"**{asset['data']['headline_en']}**")
                    # Smart Caption Generation
                    title = asset['data']['headline_en']
                    summary = asset['data'].get('summary', '')
                    
                    # Basic Keyword Matching for Tags
                    tags = ["#RacingTamizhan", "#Motorsport", "#News"]
                    if "F1" in title or "Formula 1" in title: tags.extend(["#F1", "#Formula1"])
                    if "MotoGP" in title: tags.extend(["#MotoGP", "#BikeRacing"])
                    if "Red Bull" in title: tags.append("#RedBullRacing")
                    if "Ferrari" in title: tags.append("#ScuderiaFerrari")
                    if "Hamilton" in title: tags.append("#LewisHamilton")
                    if "Verstappen" in title: tags.append("#MaxVerstappen")
                    
                    # Dynamic Prefix based on Type
                    item_type = asset['data'].get('type', 'NEWS')
                    emoji_map = {
                        "BREAKING": "🚨 BREAKING:",
                        "RESULT": "🏆 RESULT:",
                        "RUMOUR": "👀 RUMOUR:",
                        "OFFICIAL": "📝 OFFICIAL:",
                        "ANALYSIS": "🧠 ANALYSIS:",
                        "NEWS": "📰 NEWS:"
                    }
                    prefix = emoji_map.get(item_type, "📰 NEWS:")
                    
                    # COMBINED CAPTION: Prefix + Title + SUMMARY + Call to Action + Tags
                    default_caption = f"{prefix} {title}\n\n{summary}\n\nFollow @racing.tamizhan for more updates!\n\n{' '.join(tags)}"
                    
                    # Editable Caption
                    caption = st.text_area("Caption", value=default_caption, height=250, key=f"caption_{i}")
                    asset['caption'] = caption # Store for publisher
                    
                    # Approve Toggle
                    approved = st.checkbox("Approve for Upload", value=asset['approved'], key=f"approve_{i}")
                    st.session_state.generated_assets[i]['approved'] = approved

# --- TAB 3: PUBLISHER ---
with tab3:
    st.header("Agent Gamma: The Publisher")
    st.write("Upload approved assets to Social Media.")
    
    # Filter approved
    approved_list = [a for a in st.session_state.generated_assets if a['approved']]
    
    if not approved_list:
        st.info("No assets approved yet. Go to Studio tab.")
    else:
        st.write(f"Ready to upload **{len(approved_list)}** assets.")
        
        # Credentials Check
        ig_user = os.getenv("IG_USERNAME")
        if not ig_user:
            st.error("Missing IG_USERNAME in .env")
        
        if st.button("🚀 Launch Publish Sequence", type="primary", disabled=(not ig_user)):
            st.write("Initializing Publisher...")
            
            # Login (Mock or Real)
            with st.spinner("Logging into Instagram..."):
                login_success = st.session_state.publisher.login_instagram(ig_user, os.getenv("IG_PASSWORD"))
            
            if not login_success:
                st.error("❌ Instagram Login Failed. Check credentials in .env")
            else:
                st.success("✅ Instagram Login Successful!")
                
                for asset in approved_list:
                    # Handle list of paths for display
                    display_name = asset['path'][0] if isinstance(asset['path'], list) else asset['path']
                    st.write(f"Uploading {os.path.basename(display_name)}...")
                    
                    # Call publisher real methods here
                    upload_success = False
                    caption = asset.get('caption', 'No caption')
                    
                    if asset['type'] == 'image':
                         upload_success = st.session_state.publisher.upload_instagram_photo(asset['path'], caption)
                    elif asset['type'] == 'video':
                         # Upload to Insta Reel AND YouTube Short
                         st.write(f"  - Uploading Reel...")
                         r1 = st.session_state.publisher.upload_instagram_reel(asset['path'], caption)
                         
                         st.write(f"  - Uploading YouTube Short...")
                         r2 = st.session_state.publisher.upload_youtube_short(asset['path'], asset['data']['headline_en'], caption)
                         
                         upload_success = r1 or r2 # Success if at least one works? or both? Let's say one.
                    
                    if upload_success:
                        st.success(f"✅ Uploaded: {asset['data']['headline_en']}")
                        # Auto-Cleanup: Remove file and remove from list
                        try:
                            if os.path.exists(asset['path']):
                                os.remove(asset['path'])
                                st.write(f"🗑️ Cleaned up local file.")
                        except Exception as e:
                            st.warning(f"Could not delete file: {e}")
                        
                        # Remove from session state
                        st.session_state.generated_assets.pop(i)
                        st.rerun() # Rerun to refresh the list immediately
                    else:
                        st.error(f"❌ Failed to upload: {asset['data']['headline_en']}")
                    
                st.balloons()
