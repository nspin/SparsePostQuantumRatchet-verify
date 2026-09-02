let
  pkgs = import ../../../cfg/nixpkgs {};
in
with pkgs;
mkShell {
  packages = [
    protobuf
  ];
}
