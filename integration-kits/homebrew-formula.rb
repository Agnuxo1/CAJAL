class CajalP2pclaw < Formula
  desc "Local scientific paper generation model"
  homepage "https://github.com/Agnuxo1/CAJAL"
  url "https://github.com/Agnuxo1/CAJAL/archive/v1.0.0.tar.gz"
  sha256 "PLACEHOLDER"
  license "MIT"

  depends_on "python@3.12"

  resource "torch" do
    url "https://files.pythonhosted.org/packages/source/t/torch/torch-2.2.0.tar.gz"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"cajal", "--version"
  end
end
