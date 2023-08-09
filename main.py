import streamlit as st
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_bool_dtype,
)

CATEGORY_HEADERS = [
    "Req Quality",
    "Req Complexity",
    "Gherkin Quality",
    "Gherkin Complexity",
    "Status",
    "Scenario_Type",
    "Domain",
    "Execution_Type",
    "Token Size Category",
]


@st.cache_data
def read_file(content, type: str) -> pd.DataFrame:
    """this function reads the contents of uploaded file and returns a dataframe"""

    if type == "xlsx":
        df = pd.read_excel(content)

    elif type == "csv":
        df = pd.read_csv(content)

    return df.loc[:, ~df.columns.str.match("Unnamed")]


@st.cache_data
def apply_filters(df: pd.DataFrame, type: str, user_input, column: str) -> pd.DataFrame:
    """this function applies filters to the dataframe based on user inputs"""

    if type == "categorical":
        return df[df[column].isin(user_input)]

    elif type == "boolean":
        if user_input == "Both":
            return df

        return df[df[column] == user_input]

    elif type == "numeric":
        return df[df[column].between(*user_input)]

    else:
        return df[df[column].str.contains(user_input)]


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """this function filters dataframe creates user interaction widgets
    and filters it based on user input"""

    df = df.copy()
    modification_container = st.container()

    with modification_container:
        filter_columns = df.columns

        for column in filter_columns:
            if is_categorical_dtype(df[column]):
                user_categorical_input = col2.multiselect(
                    f"Values for {column}: ",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )

                df = apply_filters(
                    df=df,
                    type="categorical",
                    user_input=user_categorical_input,
                    column=column,
                )

            elif is_bool_dtype(df[column]):
                user_checkbox_input = col2.radio(
                    f"Values for {column}: ", options=("Both", True, False)
                )

                df = apply_filters(
                    df=df, type="boolean", user_input=user_checkbox_input, column=column
                )

            elif is_numeric_dtype(df[column]):
                min_value = float(df[column].min())
                max_value = float(df[column].max())
                step = (max_value - min_value) / 100

                user_number_input = col2.slider(
                    f"Values for {column}: ",
                    min_value,
                    max_value,
                    (min_value, max_value),
                    step,
                )

                df = apply_filters(
                    df=df, type="numeric", user_input=user_number_input, column=column
                )

            else:
                user_text_input = col2.text_input(
                    f"Substring or regex in {column}: ",
                )

                if user_text_input:
                    df = apply_filters(
                        df=df, type="text", user_input=user_text_input, column=column
                    )

    return df


if __name__ == "__main__":
    st.set_page_config(page_title="Data Annotation Tool", layout="wide")

    uploaded_file = st.sidebar.file_uploader(
        "Upload your files here", type=["xlsx", "csv"]
    )

    col1, col2 = st.columns([8, 2])
    col1.subheader("Data:")
    col2.subheader("Filters:")

    if uploaded_file is not None:
        extension = uploaded_file.name.split(".")[-1]

        df = read_file(content=uploaded_file, type=extension)

        for header in CATEGORY_HEADERS:
            df[header] = df[header].astype("category")

        filtered_df = col1.data_editor(data=filter_dataframe(df), height=540)

    else:
        col1.write("Please upload a CSV/EXCEL file")
        col2.write("upload files to see possible filters")
