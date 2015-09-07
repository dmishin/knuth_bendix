{TabSet} = require "./tabs.coffee"

tabs = new TabSet
tabs.add "tab1", "content1"
tabs.add "tab2", "content2"
tabs.add "tab3", "content3"
tabs.add "tab4", "content4"

tabs.tabs[0].activate()
