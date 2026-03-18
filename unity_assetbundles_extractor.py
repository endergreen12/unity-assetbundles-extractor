import UnityPy
import argparse
import os

parser = argparse.ArgumentParser(
    usage=f"python {os.path.basename(__file__)} <input_folder_path> <output_folder_path>",
    add_help=True
)

parser.add_argument("input_folder_path", type=str, help="Path to input folder")
parser.add_argument("output_folder_path", type=str, help="Path to output folder")

args = parser.parse_args()

for root, dirs, files in os.walk(args.input_folder_path):
    for file in files:
        bundle_path = os.path.join(root, file)
        try:
            env = UnityPy.load(bundle_path)

            for path, obj in env.container.items():
                try:
                    data = obj.deref_parse_as_object()
                    os_path = os.path.join(args.output_folder_path, *path.split('/'))
                    os_path_dirname = os.path.dirname(os_path)
                    os.makedirs(os_path_dirname, exist_ok=True)

                    match obj.type.name:
                        case "Texture2D" | "Sprite":
                            data.image.save(os.path.splitext(os_path)[0] + ".png")
                        case "TextAsset":
                            with open(os.path.join(os_path_dirname, data.m_Name), "wb") as f:
                                f.write(data.m_Script.encode("utf-8", "surrogateescape"))
                        case "AudioClip":
                            for name, clip_data in data.samples.items():
                                with open(os.path.join(os_path_dirname, name), "wb") as f:
                                    f.write(clip_data)
                        case "Font":
                            if data.m_FontData:
                                extension = ".ttf"
                                if data.m_FontData[0:4] == b"OTTO":
                                    extension = ".otf"

                            with open(os.path.join(os_path_dirname, data.m_Name + extension), "wb") as f:
                                f.write(bytearray(data.m_FontData)) # UnityPyのドキュメントではbytearrayに変換してないけどm_FontDataはlistなのでそのままだと例外発生、前はこんなことしなくてよかったはずなんだけど
                        case "Mesh":
                            with open(os.path.join(os_path_dirname, f"{data.m_Name.replace('"', '')}.obj"), "wt", newline = "") as f:
                                # newline = "" is important
                                f.write(data.export())
                except Exception as e:
                    print("bundle: " + bundle_path)
                    print("path: " + path)
                    print(e)
                    print()
        except Exception as e:
            print(bundle_path)
            print(e)
            print()