import streamlit as st
from src.db.data_base import (
    get_daily_metrics,
    simulated_result_of_weeks,
    simulated_result_of_months
)
from src.agents.executive_agent import run_executive_agent
from src.agents.investigator_agent import investigate