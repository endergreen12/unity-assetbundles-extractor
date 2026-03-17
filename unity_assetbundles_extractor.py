import UnityPy
import glob
import os

from UnityPy.classes import AudioClip, Mesh, TextAsset

required_unitypy_version = '1.20.17'
if UnityPy.__version__ != required_unitypy_version:
    raise ImportError(f"Invalid UnityPy version detected. Please use version {required_unitypy_version}")

export_target_type_array = ["Texture2D", "Sprite", "AudioClip", "Mesh", "TextAsset"]

path = input("Enter the path that contains AssetBundles: ").replace("\"", "")
output_path = input("Enter the path to output: ").replace("\"", "")
UnityPy.config.FALLBACK_UNITY_VERSION = input("Enter the version for fallback: ")
print("Copying start")
print("If an exception occurs during copying, the log is displayed but the process is not aborted")
print()

for bundle_path in glob.glob(os.path.join(path, "*")):
    env = UnityPy.load(bundle_path)
    
    for path, obj in env.container.items():
        try:
            if not obj.type.name in export_target_type_array:
                continue
            
            full_path_dir_str = os.path.join(output_path, *path.split("/")[:-1]) # ファイル名を除いたフルパス
            os.makedirs(full_path_dir_str, exist_ok=True) # フォルダを作る
            
            data = obj.read()
            match obj.type.name:
                case "Texture2D" | "Sprite":
                    data.image.save(os.path.join(full_path_dir_str, data.m_Name + ".png")) # 拡張子がPSDだと例外が出るのでsplitextで拡張子をのぞいたパスに.pngをくっつけて保存
                    
                case "AudioClip":
                    for name, audio_data in data.samples.items():
                        with open(os.path.join(full_path_dir_str, name), "wb") as f:
                            f.write(audio_data)
                        
                case "Mesh":
                    with open(os.path.join(full_path_dir_str, f"{data.m_Name}.obj"), "wt", newline = "") as f:
                        # newline = "" is important
                        f.write(data.export())
                        
                case "TextAsset":
                    with open(os.path.join(full_path_dir_str, data.m_Name), "wb") as f:
                        f.write(data.m_Script.encode("utf-8", "surrogateescape"))
                    
        except Exception as e:
            print(f"Exception occurred while exporting {data.m_Name}")
            if hasattr(env, "file"):
                print(f"Bundle file name: {env.file.name}")
            print(f"Asset type: {obj.type.name}")
            print("Exception details:")
            print(e)
            print()
            
print("Done")