import h5py
import json

def fix_h5(file_path):
    try:
        with h5py.File(file_path, 'r+') as f:
            if 'model_config' in f.attrs:
                model_config = f.attrs.get('model_config')
                if model_config is None:
                    print("No model_config found")
                    return
                    
                # In some h5py versions, it might not be decoded
                config_str = model_config
                if isinstance(config_str, bytes):
                    config_str = config_str.decode('utf-8')
                    
                config = json.loads(config_str)
                
                # Traverse config and remove 'quantization_config'
                def traverse_and_remove(d):
                    if isinstance(d, dict):
                        if 'quantization_config' in d:
                            del d['quantization_config']
                        for k, v in d.items():
                            traverse_and_remove(v)
                    elif isinstance(d, list):
                        for item in d:
                            traverse_and_remove(item)
                            
                traverse_and_remove(config)
                
                new_config_str = json.dumps(config)
                if isinstance(model_config, bytes):
                    new_config_str = new_config_str.encode('utf-8')
                    
                f.attrs.modify('model_config', new_config_str)
                print(f"Fixed model_config for {file_path}")
            else:
                print("No model_config found in attrs")
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

fix_h5('../model/deepshield_mobilenet_image.h5')
