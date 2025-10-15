import os
import subprocess


# print(files)

def upload():
    files = os.listdir("data")
    for hand_file in files:
        cmd = rf'curl -X POST "https://poker-api.caduceus.lol/api/v1/upload" -F "file=@{os.path.abspath(f"data/{hand_file}")}"'

        print(cmd)

        os.system(cmd)

    # break


def clean_names():
    files = os.listdir("data")
    for hand_file in files:
        cmd = rf'mv "{os.path.abspath(f"data/{hand_file}")}"  "{os.path.abspath(f"data/{hand_file}").replace(",", ".")}" '

        os.system(cmd)

if __name__ == "__main__":
    # clean_names()
    upload()