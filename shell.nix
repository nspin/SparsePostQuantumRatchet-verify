let
  pkgs = import <nixpkgs> {};
in
with pkgs;
mkShell {
  packages = [
    protobuf
  ];
}
