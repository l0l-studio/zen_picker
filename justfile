build:
    cd zen_lib && cargo build

update: build
    cp ./zen_lib/target/debug/lib_zen.so ./lib_zen.so
