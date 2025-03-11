import pandas as pd
import numpy as np
import glob
import os


class MevToCsv:
    def __init__(self, mev_path, csv_path=None, quality_score=True, write_to_csv=False):
        """
        Convert a .mev file to a .csv file.
        """
        self.mev_path = mev_path
        self.csv_path = csv_path
        self.quality_score = quality_score
        self.write_to_csv = write_to_csv
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
        self, dataframe
    ) -> pd.DataFrame:  # Check that necessary columns are present
        required_columns = ["IA", "IB", "FeatName"]
        if not all(col in dataframe.columns for col in required_columns):
            raise ValueError(f"Missing required columns: {', '.join(required_columns)}")

        # Create quality score if quality_score is True
        if self.quality_score:
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
        if self.quality_score:
            expression_matrix["log2_expression"] *= expression_matrix["quality_score"]

        expression_matrix = expression_matrix[["FeatName", "log2_expression"]]
        expression_matrix["log2_expression"] = expression_matrix[
            "log2_expression"
        ].fillna(0)
        expression_matrix.rename(
            columns={"log2_expression": f"{self.sample_identifier}"}, inplace=True
        )
        return expression_matrix

    def convert(self):
        mev_header = self.read_mev_header(self.mev_path)
        df = self.read_mev_data(self.mev_path)
        expression_matrix = self.create_expression_matrix(df)
        if self.write_to_csv:
            expression_matrix.to_csv(self.csv_path, index=False)
        return mev_header, expression_matrix


class ExpressionMatrixBuilder:
    def __init__(
        self, mev_paths, csv_paths=None, quality_score=True, write_to_csv=True
    ):
        self.mev_paths = mev_paths
        self.csv_paths = csv_paths
        self.quality_score = quality_score
        self.write_to_csv = write_to_csv
        self.headers = []
        self.expression_matrices = []

    @classmethod
    def paths_builder(cls, folder, suffix=".mev"):
        """Generates mev_paths from a directory."""
        mev_paths = sorted(glob.glob(os.path.join(folder, f"*{suffix}")))
        return mev_paths

    def read_mevs(self):
        for mev_path in self.mev_paths:
            mev_to_csv = MevToCsv(
                mev_path,
                csv_path=None,
                quality_score=self.quality_score,
                write_to_csv=False,
            )
            mev_header, expression_matrix = mev_to_csv.convert()
            self.headers.append(mev_header)
            self.expression_matrices.append(expression_matrix)
        return self.headers, self.expression_matrices

    def merge_mevs(self):
        merged_expression_matrix = pd.concat(
            self.expression_matrices, axis=1, join="outer"
        )

        # Check for duplicate samples/columns
        duplicate_columns = merged_expression_matrix.columns[
            merged_expression_matrix.columns.duplicated()
        ]
        if not duplicate_columns.empty:
            warning_samples = ", ".join(duplicate_columns)
            print(f"⚠️ Warning: Duplicate sample identifiers found: {warning_samples}")
            # Remove duplicate columns, keeping only the first occurrence
            merged_expression_matrix = merged_expression_matrix.loc[
                :, ~merged_expression_matrix.columns.duplicated()
            ]

        # Count and fill NA values
        na_count = merged_expression_matrix.isna().sum().sum()
        if na_count > 0:
            print(f"⚠️ {na_count} missing values were filled with 0.")
            merged_expression_matrix.fillna(0, inplace=True)

        return merged_expression_matrix

    def save_merged_matrix(self, output_path, index=False):
        """Save the merged expression matrix to a CSV file."""
        merged_matrix = self.merge_mevs()
        merged_matrix.to_csv(output_path, index=index)
        return merged_matrix


def process_mev_folder(input_folder, output_path, quality_score=True, index=False):
    """
    Process all .mev files in a folder and create a single merged expression matrix.

    Parameters:
    -----------
    input_folder : str
        Path to folder containing .mev files
    output_path : str
        Path where the merged matrix will be saved
    quality_score : bool, default=True
        Whether to apply quality scoring

    Returns:
    --------
    pandas.DataFrame
        The merged expression matrix
    """
    mev_paths = ExpressionMatrixBuilder.paths_builder(input_folder)
    builder = ExpressionMatrixBuilder(mev_paths, quality_score=quality_score)
    _, _ = builder.read_mevs()
    merged_matrix = builder.merge_mevs()
    builder.save_merged_matrix(output_path, index=index)
    return merged_matrix
