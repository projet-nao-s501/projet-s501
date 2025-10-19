
sudo apt install git cmake build-essential python3 python3-pip -y
git clone https://github.com/aldebaran/libqi.git
git clone https://github.com/aldebaran/libqi-python.git
pip install conan
conan profile detect
QI_VERSION="4.0.5"
cd libqi-python
conan export ../libqi --version "${QI_VERSION}"
conan install . -s build_type=Release --profile=default --build=missing -c tools.build:skip_test=true -c tools.build:jobs=4
cmake --preset conan-linux-x86_64-gcc-release
cmake --build --preset conan-linux-x86_64-gcc-release
PYTHON_LIB_PATH=$(python3 -c "import sysconfig; print(sysconfig.get_path('purelib'))")
cmake --install build/linux-x86_64-gcc-release/ --component Module --prefix "${PYTHON_LIB_PATH}/"
cd ..