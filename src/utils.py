import os


class Utils:

    @staticmethod
    def generate_file_name(table_match_half1, table_match_half2):
        return (
                str(table_match_half1.start_time_stamp)
                .replace("-", "_")
                .replace(":", "_")
                + "_" + str(table_match_half1.id)
                + "_" + str(table_match_half2.id)
                + "@" + table_match_half1.map_name
        )

    @staticmethod
    def test_file_creation(output_dir):

        test_filename = "write_check.tmp"
        test_filepath = os.path.join(output_dir, test_filename)

        # Remove the test file if it already exists
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

        with open(test_filepath, "w") as f:
            f.write("write check")

        if not os.path.exists(test_filepath):
            success = False
        else:
            success = True

        os.remove(test_filepath)

        return success
