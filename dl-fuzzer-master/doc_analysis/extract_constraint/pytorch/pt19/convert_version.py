import os
import yaml

dirs = ["changed", "unchanged"]
for dir in dirs:
    api_file_names = os.listdir(dir)
    # print(api_file_names)
    for api_file_name in api_file_names:
        api_file_path = os.path.join(dir, api_file_name)
        with open(api_file_path, "r") as file:
            api_file = yaml.safe_load(file)
        print(api_file)
        api_file["version"] = "1.9.0"
        print(api_file)
        with open(api_file_path, "w") as file:
            yaml.dump(api_file, file)
            # break
