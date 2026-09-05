{
  inputs = {
    nixpkgs.follows = "aeneas/nixpkgs";
    flake-utils.follows = "aeneas/flake-utils";
    charon.follows = "aeneas/charon";
    aeneas.url = "github:AeneasVerif/aeneas/nightly-2026.08.27-5b9dcf3";
  };

  outputs = inputs @ { self, nixpkgs, flake-utils, charon, aeneas, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        charon = inputs.charon.packages.${system}.charon;
        aeneas = inputs.aeneas.packages.${system}.aeneas;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.protobuf
            pkgs.elan
            charon
            aeneas
          ];
        };
      });
}
