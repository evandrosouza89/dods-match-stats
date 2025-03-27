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
