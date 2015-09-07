
parseKeys = (keys) ->
  classes = {}
  for part in keys.split " " when part
    classes[part] = true
  return classes
  
joinKeys = (keys) ->
  [cn for cn of keys].join " "
  
addClass = (e, cls)->
  classes = parseKeys e.className
  classes[cls] = true
  e.className = joinKeys classes

removeClass = (e, cls)->
  classes = parseKeys e.className
  delete classes[cls]
  e.className = joinKeys classes
      
class Tab
  constructor: (@tabSet, trigger, content) ->
    @active = false
    @visibleStyle = "block"
    @selectedClass = "active"
    
    @triggerElem = document.getElementById trigger
    @contentElem = document.getElementById content
    @triggerElem.addEventListener "click", (e)=>
      e.preventDefault()
      @activate()
      
  activate: ->
    if not @active
      @tabSet.deactivateAll()
      @contentElem.style.display = @visibleStyle
      addClass @triggerElem, @selectedClass
      @active = true
      
  deactivate: ->
    if @active
      @contentElem.style.display = "none"
      removeClass @triggerElem, @selectedClass
      @active = false
    
exports.TabSet = class TabSet
  constructor: ->
    @tabs = []
  add: (triggerId, contentId) ->
    @tabs.push new Tab this, triggerId, contentId
  deactivateAll: ->
    for tab in @tabs
      tab.deactivate()
    return
