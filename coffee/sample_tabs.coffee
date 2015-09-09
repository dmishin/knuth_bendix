{TabSet} = require "./tabs.coffee"
{Tessellation} = require "./hyperbolic_tessellation.coffee"
M = require "./matrix3.coffee"

E = (id) -> document.getElementById id


updateTessellationIcon = ->
  n = parseInt E("tessellation-n").value, 10
  m = parseInt E("tessellation-m").value, 10

  E("tessellation-symbol").innerHTML = "{#{n}; #{m}}"
  canv = document.getElementById "tessellation-icon"
  ctx = canv.getContext "2d"
  ctx.clearRect 0, 0, canv.width, canv.height
  ctx.save()
  s = Math.min( canv.width, canv.height ) / 2 #
  try
    tess = new Tessellation n, m

    ctx.scale s, s

    ctx.translate 1, 1
    ctx.fillStyle = "black"
    ctx.lineWidth = 1.0/s
    ctx.strokeStyle = "#000"

    ctx.beginPath()
    tess.makeCellShapePoincare( M.eye(), ctx )
    for ap in [0...n]
      A = tess.group.aPower ap
      for bp in [1...m]
        B = tess.group.bPower bp
        tess.makeCellShapePoincare( M.mul(A, B), ctx )
    ctx.stroke()

  catch e
    ctx.lineWidth = s/10
    ctx.strokeStyle = "#000"
    ctx.beginPath()
    ctx.moveTo 0, 0
    ctx.lineTo s*2, s*2
    
    ctx.moveTo s*2, 0
    ctx.lineTo 0, s*2
    ctx.stroke()
    
  ctx.restore()

tabs = new TabSet
tabs.add "tab1", "content1"
tabs.add "tab2", "content2"
tabs.add "tab3", "content3"
tabs.add "tab4", "content4"


E("tessellation-n").addEventListener "change", updateTessellationIcon
E("tessellation-m").addEventListener "change", updateTessellationIcon
E("tessellation-n").addEventListener "input", updateTessellationIcon
E("tessellation-m").addEventListener "input", updateTessellationIcon

updateTessellationIcon()
tabs.tabs[3].activate()
