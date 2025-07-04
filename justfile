build:
    cd zen_lib && cargo build

release:
    cd zen_lib && cargo build -r

release_win:
    cd zen_lib; cargo build -r

update: build
    cp ./zen_lib/target/debug/lib_zen.so ./lib_zen.so

distribute: release
    cp ./zen_lib/target/release/lib_zen.so ./lib_zen.so

distribute_win: release_win
    copy ./zen_lib/target/release/_zen.dll ./lib_zen.pyd

#replace path to your krita executable
start:
    ~/AppImages/krita.appimage ./testing.kra
