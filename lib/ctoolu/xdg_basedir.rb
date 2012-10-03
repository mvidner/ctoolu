# http://standards.freedesktop.org/basedir-spec/basedir-spec-0.8.html
# "X Desktop Group" is a former name of freedesktop.org.
# API modeled after python-xdg, because xdg.gem sucks.
module XDG
  extend self

  def xdg_data_home
    ENV.fetch('XDG_DATA_HOME', "#{ENV['HOME']}/.local/share")
  end

  def xdg_data_dirs
    [xdg_data_home] +
    ENV.fetch('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
  end

  def xdg_config_home
    ENV.fetch('XDG_CONFIG_HOME', "#{ENV['HOME']}/.config")
  end

  def xdg_config_dirs
    [xdg_config_home] +
    ENV.fetch('XDG_CONFIG_DIRS', '/etc/xdg').split(':')
  end

  # @return [Array<String>] paths
  def load_data_paths(resource)
    paths = xdg_data_dirs.map { |dir| Pathname.new(dir) + resource }
    paths.select { |p| p.absolute? && p.exist? }
  end

  # @return [Array<String>] paths
  def load_config_paths(resource)
    paths = xdg_config_dirs.map { |dir| Pathname.new(dir) + resource }
    paths.select { |p| p.absolute? && p.exist? }
  end

  # @return [String, nil]
  def load_first_config(resource)
    # correctly returns nil for an empty list
    load_config_paths(resource).first
  end
end # module XDG
