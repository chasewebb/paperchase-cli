# homebrew-tap/Formula/paperchase.rb
class Paperchase < Formula
  include Language::Python::Virtualenv

  desc "PaperChase — proprietary AI operator CLI by PaperChaseLabs"
  homepage "https://paperchaselabs.com"
  url "https://files.pythonhosted.org/packages/source/p/paperchase/paperchase-0.1.0.tar.gz"
  sha256 "REPLACED_BY_RELEASE_AUTOMATION"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "paperchase, version 0.1.0", shell_output("#{bin}/paperchase --version")
  end
end
