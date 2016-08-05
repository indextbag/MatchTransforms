
def getGlobalTransform(node, tfmPlug="worldMatrix"):
	fn = om.MFnTransform(node)
	plug = fn.findPlug(tfmPlug)

	if plug.isArray():
		plug = plug.elementByLogicalIndex(0)

	mat = plug.asMObject()
	fnMat = om.MFnMatrixData(mat)

	return om.MTransformationMatrix(fnMat.matrix())


def matchTransform(nodes, source, translate=True, rotate=True, scale=True, space=om.MSpace.kWorld, matchPivot=False):
	# confirm/create MSelectionList of nodes

	if isinstance(nodes, om.MSelectionList):
		pass
	elif isinstance(nodes, om.MObject) or isinstance(nodes, om.MDagPath):
		sel = om.MSelectionList()
		sel.add(nodes)
		nodes = sel
	elif isinstance(nodes, om.MDagPathArray):
		sel = om.MSelectionList()
		for i in xrange(nodes.length()):
			sel.add(nodes[i])
		nodes = sel

	# get the proper matrix of source
	if space == om.MSpace.kWorld:
		srcTfm = getGlobalTransform(source, "worldMatrix")
	else:
		srcTfm = getGlobalTransform(source, "matrix")

	# source pos
	pos = srcTfm.getTranslation(space)

	# source pivot
	srcPivot = srcTfm.scalePivot(space)

	# stupid MScriptUtil stuff
	dagNode = om.MDagPath()
	util = om.MScriptUtil()
	util.createFromDouble(0.0, 0.0, 0.0)
	scl = util.asDoublePtr()

	fn = om.MFnTransform()
	for i in xrange(nodes.length()):
		nodes.getDagPath(i, dagNode)

		if space == om.MSpace.kObject:
			tfm = srcTfm
		else:
			# multiply the global scale and rotation by the nodes parent inverse world matrix to get local rot & scl
			invParent = getGlobalTransform(dagNode, "parentInverseMatrix")
			tfm = om.MTransformationMatrix(srcTfm.asMatrix() * invParent.asMatrix())

		# rotation
		rot = tfm.rotation()

		# scale
		tfm.getScale(scl, space)

		# Set Transforms----------------------------
		fn.setObject(dagNode)
		# set Scaling
		if scale:
			fn.setScale(scl)

		# set Rotation
		if rotate:
			fn.setRotation(rot)

		# set Translation
		if translate:
			if matchPivot:
				nodePivot = fn.scalePivot(space)
				pos += srcPivot - nodePivot

			fn.setTranslation(pos, space)