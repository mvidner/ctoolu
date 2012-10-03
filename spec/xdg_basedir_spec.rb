require 'spec_helper'
require 'ctoolu/xdg_basedir'

describe XDG do
  describe "load_data_paths" do
    it "returns default paths" do
      with_constants 'ENV' => {'HOME' => '/home/eliza'} do
#      Pathname.stub(:exist? => true)
        FileTest.stub(:exist? => true)

        XDG.load_data_paths("foo").map(&:to_s).should ==
          [
           "/home/eliza/.local/share/foo",
           "/usr/local/share/foo",
           "/usr/share/foo"
          ]
      end
    end
  end
end
