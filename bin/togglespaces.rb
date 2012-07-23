#!/usr/bin/env macruby

require "optparse"
require "ostruct"

framework "ScriptingBridge"

options = OpenStruct.new

optparse = OptionParser.new do |opts|
  opts.banner = "Usage: togglespaces.rb -v -r <rows> -c <columns>"

  opts.on('-v', '--verbose', 'output more info') do |v|
    options.verbose = v
  end

  opts.on('-r', '--rows [N]', Integer, 'number of rows to have') do |rows|
    if rows < 1
      puts "A row count > 1 is required"
      exit 1
    end
    options.rows = rows
  end

  opts.on('-c', '--columns [N]', Integer, 'number of columns to have') do |cols|
    if cols < 1
      puts "A column count > 1 is required"
      exit 1
    end
    options.cols = cols
  end
end.parse!

if options.verbose
  puts "Setting Spaces to have %s rows" % options.rows
  puts "Setting Spaces to have %s columns" % options.cols
end

events = SBApplication.applicationWithBundleIdentifier("com.apple.SystemEvents")
if options.rows != nil
  events.exposePreferences.spacesPreferences.spacesRows = options.rows
end

if options.cols != nil
  events.exposePreferences.spacesPreferences.spacesColumns = options.cols
end

if options.verbose
  puts "Successfully set Spaces preferences"
end
