#!/usr/bin/env python3
"""
Create Test PUBG Mobile PAK - ZIP Format - SuperGrok AI v1.3
Creates a demo .pak file in ZIP format for easier analysis
"""

import os
import zipfile
import json

def create_test_pubg_zip_pak():
    """Create a test PUBG Mobile .pak file in ZIP format"""
    
    # Create test directory
    os.makedirs("test_files", exist_ok=True)
    
    # Create some test content files
    test_files = {
        "Content/Textures/Player_3.9.0.dds": b"FAKE_DDS_TEXTURE_DATA_FOR_PLAYER_SKIN_3.9.0",
        "Content/Meshes/Weapon_3.9.0.fbx": b"FAKE_FBX_WEAPON_MODEL_DATA_3.9.0",
        "Content/Sounds/Weapon_3.9.0.wav": b"FAKE_WAV_WEAPON_SOUND_DATA_3.9.0",
        "Content/UI/Menu_3.9.0.png": b"FAKE_PNG_MENU_UI_DATA_3.9.0",
        "Content/Config/Game_3.9.0.json": b'{"version": "3.9.0.20139", "patch_notes": "New weapons, maps, and features"}',
        "Content/Shaders/Effect_3.9.0.shader": b"FAKE_SHADER_EFFECT_CODE_3.9.0",
        "Content/Animations/Player_3.9.0.anim": b"FAKE_ANIMATION_DATA_3.9.0",
        "Content/Particles/Explosion_3.9.0.part": b"FAKE_PARTICLE_SYSTEM_DATA_3.9.0",
        "Content/Localization/RU_3.9.0.loc": b"FAKE_RUSSIAN_LOCALIZATION_3.9.0",
        "Content/Localization/EN_3.9.0.loc": b"FAKE_ENGLISH_LOCALIZATION_3.9.0"
    }
    
    # Create test files
    for filename, content in test_files.items():
        filepath = os.path.join("test_files", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(content)
    
    # Create PAK file in ZIP format
    pak_filename = "game_patch_3.9.0.20139.pak"
    
    with zipfile.ZipFile(pak_filename, 'w', zipfile.ZIP_DEFLATED) as pak:
        for filename, content in test_files.items():
            pak.writestr(filename, content)
    
    print(f"✅ Created test PUBG Mobile PAK (ZIP): {pak_filename}")
    print(f"📁 Contains {len(test_files)} test files")
    print(f"📏 Total size: {os.path.getsize(pak_filename)} bytes")
    
    return pak_filename

if __name__ == "__main__":
    create_test_pubg_zip_pak()