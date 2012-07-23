#!/usr/bin/env macruby

require "pp"
framework "ScriptingBridge"

def configure()
  urls = (ARGV[0..-1] or [])
  puts "Lauching urls::"
  puts urls
  launch(urls)
end

def launch(urls)
  chrome = SBApplication::applicationWithBundleIdentifier('com.Google.Chrome')
  chrome.windows.push(GoogleChromeWindow.new)
  (0..urls.length - 1).each do |x|
    if x != 0
      chrome.windows[0].tabs.push(GoogleChromeTab.new)
    end
    chrome.windows[0].tabs[x].executeJavascript('window.location = "%s"' % urls[x])
  end
end

configure()
