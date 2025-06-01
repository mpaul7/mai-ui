# dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from metrics_collector import collect_metrics

st.set_page_config(page_title="System Monitor", layout="wide")

st.title("🔍 GPU & System Resource Dashboard")

mode = st.sidebar.radio("Choose Mode", ["Live Monitor", "Load CSV"])

if mode == "Live Monitor":
    duration = st.sidebar.slider("Duration (seconds)", min_value=10, max_value=600, value=60)
    interval = st.sidebar.slider("Interval (seconds)", min_value=1, max_value=5, value=1)

    if st.button("Start Monitoring"):
        with st.spinner("Collecting metrics..."):
            df = collect_metrics(duration=duration, interval=interval)

        st.success("Monitoring complete!")
        st.dataframe(df.head())

        csv_filename = f"metrics_{int(time.time())}.csv"
        df.to_csv(csv_filename, index=False)
        st.download_button("📥 Download CSV", data=df.to_csv(index=False), file_name=csv_filename)

elif mode == "Load CSV":
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
    else:
        st.stop()

# Visualization
if 'df' in locals():
    st.subheader("📊 GPU Metrics")
    st.line_chart(df.set_index("time")[["gpu_mem_used", "gpu_mem_bw", "gpu_util"]])

    st.subheader("🧠 System Memory")
    st.line_chart(df.set_index("time")[["sys_mem_used", "sys_mem_free"]])

    st.subheader("🖥️ CPU Utilization")
    cpu_cols = [col for col in df.columns if col.startswith("cpu_core_")]
    st.line_chart(df.set_index("time")[["cpu_util"] + cpu_cols])
