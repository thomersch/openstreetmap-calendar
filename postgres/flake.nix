{
  description = "A flake that adds the postgis extension to Postgresql";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages = {
          # Return postgrsql with the postgis extension include.
          postgresql = pkgs.postgresql_15.withPackages (p: [ p.postgis ]);
        };

        defaultPackage = self.packages.postgresql;
      });
}
