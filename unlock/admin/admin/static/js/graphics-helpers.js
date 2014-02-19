function SceneJSHelper(){}

SceneJSHelper.prototype.createCheckerBoardNode = function(nRows, nCols)
{
	var board = [];

	// 1st square is black
	var color = 0;
	
	var i = 0;
	for (var x=0; x<nCols; x++)
	{
		// From the second column onwards, if number of rows is even,
		// the next square will have the same color as its neighbor on the left,
		// so we change it again
		color = (nRows%2==0 && x>0) ? 1-color : color;
		
		for (var y=0; y<nRows; y++)
		{
			// Scene node definiton for this square
			var square = {
				type:"geometry",
				primitive:"triangle-strip",										
				positions:[
					x+1,y,0,
					x+1,y+1,0,													
					x,y,0,
					x,y+1,0
				],
				colors:[
					color, color, color, 1,
					color, color, color, 1,
					color, color, color, 1,
					color, color, color, 1,
				],
				indices:[
					0, 1, 2, 3
				]
			};
			
			// Add square to board
			board[i] = square;
			i++;
			
			// Change color for next square
			color = 1 - color;
		}
	}
	
	return board;
}

SceneJSHelper.prototype.setFlickeringScene = function(scene, rootID, frate)
{
	scene.getNode(rootID, function (node) {
		setInterval(function () {
			node.setEnabled(!node.getEnabled());					
		}, 1000/frate);
	});
}