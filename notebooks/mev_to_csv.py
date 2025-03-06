import pandas as pd
import numpy as np


class MevToCsv:
    def __init__(self, mev_path, csv_path, quality_score=True):
        """
        Convert a .mev file to a .csv file.
        """
        self.mev_path = mev_path
        self.csv_path = csv_path
        self.quality_score = quality_score
        self.dataframe = None

    @property
    def sample_identifier(self) -> str:
        sample_identifier = self.mev_path.split("/")[-1].split(".")[0]
        return sample_identifier

    @classmethod
    def read_mev_header(cls, mev_path):
        with open(mev_path, "r") as f:
            mev_header = {}
            for i in range(7):
                line = f.readline().replace("#", "").strip()
                key, value = line.split(":", 1)
                mev_header[key] = value.strip()
        return mev_header

    @classmethod
    def read_mev_data(cls, mev_path, skiprows=8):
        ## read the data from the file
        # skiprows=8 to skip the header ## potential that all mev files have the same header number of rows
        df = pd.read_csv(mev_path, sep="\t", skiprows=skiprows)
        return df

    @classmethod
    def create_quality_score(cls, row):
        # scoring system to create a 1 for good reads and 0 for reads to be omitted
        # other reads are arbitrary for now
        if row["FlagA"] == "Y" and row["FlagB"] == "Y":
            return 1.0  # Highest quality
        elif row["FlagA"] in ["X", "B", "A"] or row["FlagB"] in ["X", "B", "A"]:
            return 0.0  # Poor quality, consider excluding
        elif row["FlagA"] == "C" or row["FlagB"] == "C":
            return 0.5  # Compromised but potentially usable
        elif row["FlagA"] == "Z" or row["FlagB"] == "Z":
            return 0.3  # Near background, low confidence
        else:
            return 0.8  # Other flags

    def create_expression_matrix(
        self, dataframe, sample_identifier, quality_score
    ):  # Check that necessary columns are present
        required_columns = ["IA", "IB", "FeatName"]
        if not all(col in dataframe.columns for col in required_columns):
            raise ValueError(f"Missing required columns: {', '.join(required_columns)}")

        # Create quality score if quality_score is True
        if quality_score:
            dataframe["quality_score"] = dataframe.apply(
                lambda row: self.create_quality_score(row), axis=1
            )
            excluded_samples = dataframe[dataframe["quality_score"] <= 0]
            if not excluded_samples.empty:
                print(
                    f"Excluded {len(excluded_samples)} samples due to low quality scores."
                )
            dataframe = dataframe[
                dataframe["quality_score"] > 0
            ]  # Exclude poor quality samples

        # Calculate expression values
        expression_matrix = dataframe.copy()

        # Calculate log2 expression with pseudocount
        expression_matrix["log2_expression"] = np.log2(
            (expression_matrix["IA"] / expression_matrix["IB"]) + 1
        )

        # Multiply by quality score in place if quality_score is True
        if quality_score:
            expression_matrix["log2_expression"] *= expression_matrix["quality_score"]

        expression_matrix = expression_matrix[["FeatName", "log2_expression"]]
        expression_matrix["log2_expression"] = expression_matrix[
            "log2_expression"
        ].fillna(0)
        expression_matrix.rename(
            columns={"log2_expression": f"{sample_identifier}"}, inplace=True
        )
        return expression_matrix

    def convert(self):
        mev_header = self.read_mev_header(self.mev_path)
        df = self.read_mev_data(self.mev_path)
        expression_matrix = self.create_expression_matrix(
            df, self.sample_identifier, self.quality_score
        )
        expression_matrix.to_csv(self.csv_path, index=False)
        return mev_header, expression_matrix
