$:.unshift File.expand_path("../../lib", __FILE__)

RSpec.configure do |c|
  c.color_enabled = true
end

def silence_warnings
  v = $VERBOSE
  $VERBOSE = nil
  yield
ensure
  $VERBOSE = v
end

# http://digitaldumptruck.jotabout.com/?p=551
def with_constants(constants, &block)
  saved_constants = {}
  constants.each do |constant, val|
    saved_constants[ constant ] = Object.const_get( constant )
    silence_warnings do
      Object.const_set( constant, val )
    end
  end
 
  begin
    block.call
  ensure
    constants.each do |constant, val|
      silence_warnings do
        Object.const_set( constant, saved_constants[ constant ] )
      end
    end
  end
end
