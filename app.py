import os
import streamlit as st
from PIL import Image
from image_preprocessor import ImagePreprocessor

DATA_PATH_KEY = "data_path"

st.title("Duplicate Image Cleaner")

# region Load data
col1, _ = st.columns(2)
data_path = col1.text_input("Enter the path to your image directory:", value="data")

if DATA_PATH_KEY not in st.session_state or st.session_state[DATA_PATH_KEY] != data_path:
    st.session_state[DATA_PATH_KEY] = data_path
    st.session_state.duplicate_groups = {}
    st.session_state.no_duplicates = False

if "duplicate_groups" not in st.session_state:
    st.session_state.duplicate_groups = {}

if "no_duplicates" not in st.session_state:
    st.session_state.no_duplicates = False

if not data_path or not os.path.isdir(data_path):
    st.warning("Please enter a valid directory path containing images.")
    st.stop()


image_preprocessor = ImagePreprocessor(data_path)
# endregion

# region Image Groups
st.header("Find Groups of Similar Images")

if st.session_state.duplicate_groups:
    st.write(f"Found **{len([x for xs in st.session_state.duplicate_groups.values() for x in xs])}** duplicates.")
st.write(f"**{len(image_preprocessor.files)}** total files in **{data_path}**.")

col1, col2 = st.columns(2)
if col1.button("Find Duplicates"):
    st.session_state.duplicate_groups = image_preprocessor.find_all_duplicates()
    if not len(st.session_state.duplicate_groups):
        st.session_state.no_duplicates = True
    st.rerun()
if st.session_state.no_duplicates:
    col1.info("No duplicates found.")
if st.session_state.duplicate_groups and col2.button("Clear Duplicates"):
    for files in st.session_state.duplicate_groups.values():
        image_preprocessor.deduplicate_group(files)
    st.session_state.duplicate_groups = {}
    st.rerun()
if st.session_state.duplicate_groups:
    if not st.session_state.duplicate_groups:
        st.info("No duplicates found.")
    else:
        st.header("Duplicate Groups")
        for idx, (file_hash, files) in enumerate(st.session_state.duplicate_groups.items()):
            with st.expander(f"{len(files)} items, Group {file_hash}", expanded=idx == 0):
                if st.button("Delete Group", key=f"delete_group_{file_hash}"):
                    st.session_state.duplicate_groups.pop(file_hash)
                    image_preprocessor.deduplicate_group(files)
                    st.rerun()
                files_list = list(files)
                num_columns = 5
                rows = [files_list[i: i + num_columns] for i in range(0, len(files_list), num_columns)]
                for row in rows:
                    cols = st.columns(len(row))
                    for idx, file in enumerate(row):
                        image_path = os.path.join(data_path, file)
                        try:
                            image = Image.open(image_path)
                            cols[idx].image(image, caption=file, use_container_width=True)
                            if cols[idx].button("Delete", key=f"delete_img_{file}"):
                                st.session_state.duplicate_groups[file_hash].remove(file)
                                if len(st.session_state.duplicate_groups[file_hash]) == 1:
                                    st.session_state.duplicate_groups.pop(file_hash)
                                image_preprocessor.delete_file(file)
                                st.rerun()
                        except Exception as e:
                            cols[idx].write(f"Error loading {file}: {e}")
# endregion

# region Single Images

st.header("Find Similar Images")
col1, col2 = st.columns(2)
with col1:
    selected_file = st.selectbox("Select an image", image_preprocessor.files, index=None)
if selected_file:
    with col2:
        selected_image_path = os.path.join(data_path, selected_file)
        try:
            selected_image = Image.open(selected_image_path)
            st.image(selected_image, caption=f"Selected Image ({selected_file})", use_container_width=True)
        except Exception as e:
            st.write(f"Error loading the selected image {selected_file}: {e}")

    similar_files = list(image_preprocessor.yield_similar(selected_file))
    if not similar_files:
        st.info("No similar images found.")
    else:
        st.subheader("Similar Images")
        num_columns = 5
        rows = [similar_files[i: i + num_columns] for i in range(0, len(similar_files), num_columns)]
        for row in rows:
            cols = st.columns(len(row))
            for idx, file in enumerate(row):
                image_path = os.path.join(data_path, file)
                try:
                    image = Image.open(image_path)
                    cols[idx].image(image, caption=file, use_container_width=True)
                except Exception as e:
                    cols[idx].write(f"Error loading {file}: {e}")

# endregion
