{ lib, python3Packages, fetchFromGitHub }:

python3Packages.buildPythonApplication rec {
  pname = "cajal-p2pclaw";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "Agnuxo1";
    repo = "CAJAL";
    rev = "v${version}";
    sha256 = "PLACEHOLDER";
  };

  propagatedBuildInputs = with python3Packages; [
    torch
    transformers
    fastapi
    uvicorn
    pydantic
  ];

  meta = with lib; {
    description = "Local scientific paper generation model";
    homepage = "https://github.com/Agnuxo1/CAJAL";
    license = licenses.mit;
    maintainers = [ maintainers.agnuxo1 ];
  };
}
