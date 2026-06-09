# src/core/save_diff.py
import logging

logger = logging.getLogger("core.save_diff")

class SaveDiff:
    @staticmethod
    def compare(dict_a: dict, dict_b: dict, path_context: str = "") -> list:
        """Recursively parses two data streams dictionary matrices structures to locate variations."""
        discrepancies = []

        # Parse key structural parameters elements
        all_keys = set(dict_a.keys()).union(set(dict_b.keys()))

        for key in all_keys:
            current_path = f"{path_context}.{key}" if path_context else key

            # Capture elements presence variations mutations
            if key not in dict_a:
                discrepancies.append({"path": current_path, "old": None, "new": dict_b[key]})
                continue
            if key not in dict_b:
                discrepancies.append({"path": current_path, "old": dict_a[key], "new": None})
                continue

            val_a = dict_a[key]
            val_b = dict_b[key]

            # Deep dive checks into embedded nested sub-dictionaries records
            if isinstance(val_a, dict) and isinstance(val_b, dict):
                discrepancies.extend(SaveDiff.compare(val_a, val_b, current_path))
            
            # Handle sequence list components elements comparisons
            elif isinstance(val_a, list) and isinstance(val_b, list):
                if val_a != val_b:
                    # For performance and clarity, report variations as direct assignments configurations profiles
                    discrepancies.append({"path": current_path, "old": val_a, "new": val_b})
            
            # Verify basic element primitives values mutations changes
            elif val_a != val_b:
                discrepancies.append({"path": current_path, "old": val_a, "new": val_b})

        return discrepancies

    @staticmethod
    def pretty_print(discrepancies_list: list) -> str:
        """Formats an extracted variations profile array into high visibility console output layouts."""
        if not discrepancies_list:
            return "No behavioral mutations detected between target data streams."

        output_lines = []
        for update_item in discrepancies_list:
            output_lines.append(f"{update_item['path']}")
            output_lines.append(f"  {update_item['old']} -> {update_item['new']}\n")
            
        return "\n".join(output_lines).strip()