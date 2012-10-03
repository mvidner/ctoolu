# -*- ruby-*-

require 'ostruct'
require 'pathname'

desc "Install the application for this user"
task :install_user do
  ctoolu_install USER_DIRS
end

desc "Install the application for systemwide use"
task :install do
  ctoolu_install SYSTEM_DIRS
end

desc "Run the application from the working copy"
task :run do
  sh 'XDG_CONFIG_HOME=`pwd`/config XDG_DATA_HOME=`pwd`/data RUBYLIB=lib ./ctoolu'
end

# FIXME, this is not exactly following 
# http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
HOME = ENV['HOME']
USER_DIRS = {
  "bin" => "#{HOME}/bin",
  "xdg_config" => "#{HOME}/.config",
  "xdg_data" => "#{HOME}/.local/share",
}
SYSTEM_DIRS = {
  "bin" => "/usr/bin",
  "xdg_config" => "/etc/xdg",
  "xdg_data" => "/usr/share",
}

# calls FileUtils.install
# but assumes the target is a directory and ensures it exists
# Option :pkill will kill the program that was installed
# (assuming it will get restarted somehow)
# Option :config will take care not to overwrite an existing file,
#   appending .new to the installed one.
def dir_install(source, target_dir, options={})
  pkill = options.delete :pkill
  config = options.delete :config

  mkdir_p target_dir, options.merge({:mode => nil})
  
  target = target_dir
  if config
    target << '/' << Pathname.new(source).basename.to_s
    if File.exist? target
      target << ".new"
    end
  end
  install source, target, options

  if pkill
    # Pkill never kills itself, good.
    # The variable references ensure it doesn't kill its parent shell, duh.
    sh "TD=#{target_dir}; S=#{source}; pkill -f $TD/$S || true"
  end
end

# installs ctoolu, using a hash defining the base directories
def ctoolu_install(dirs)
  # make ostruct from hash for easier access
  dirs = OpenStruct.new(dirs) unless dirs.respond_to? :bin

  dir_install "ctoolu", dirs.bin, :mode => 0755, :pkill => true
  dir_install "ctoolu-activate", dirs.bin, :mode => 0755
  dir_install "ctoolu.desktop", dirs.xdg_config + "/autostart"
  dir_install "config/ctoolu.yaml", dirs.xdg_config, :config => true
  Dir.glob("data/ctoolu/*.yaml") do |rule|
    dir_install rule, dirs.xdg_data + "/ctoolu"
  end
  dir_install "clipboard-relay", dirs.bin, :mode => 0755, :pkill => true
  dir_install "net.vidner.ClipboardRelay.service", dirs.xdg_data + "/dbus-1/services"
end
