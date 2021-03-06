import unittest
from vrml.vrml97 import nodepath
from vrml.vrml97.basenodes import Transform
from vrml.arrays import allclose, array, pi,dot

class TestNodePath( unittest.TestCase ):
    def setUp( self ):
        self.empty = nodepath.NodePath()
        self.first_child = self.empty + [ Transform( translation=(1,0,0), DEF='first', ) ]
        self.second_child = self.first_child + [ Transform( translation=(1,0,0), DEF='second') ]
        self.third_child = self.second_child + [ Transform( translation=(3,0,0), scale=(2,1,2), rotation=(0,1,0,pi/2), DEF='third',)]
        self.fourth_child = self.third_child + [ Transform( DEF='fourth',) ]
    def test_empty_matrix( self ):
        m = self.empty.transformMatrix()
        assert allclose( 
            m,
            array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],'f')
        ), m
    def test_second_child( self ):
        m = self.second_child.transformMatrix()
        assert allclose( 
            m,
            array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[2,0,0,1]],'f')
        ), m
    def test_change_translation( self ):
        self.first_child[-1].translation = (-1,0,0)
        m2 = self.second_child.transformMatrix()
        assert allclose( 
            m2,
            array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],'f')
        ), m2
    def test_change_rotation( self ):
        self.first_child[-1].rotation = (0,1,0,3.14)
        m = self.second_child.transformMatrix( translate=False, scale=False)
        self.first_child[-1].rotation = (0,1,0,0.0)
        m2 = self.second_child.transformMatrix( translate=False, scale=False)
        assert not allclose( m,m2 ), (m,m2)
    
    def test_iterchildren( self ):
        l = list( self.first_child.iterchildren())
        assert l == [ self.second_child ]
    def test_iterdescendents( self ):
        l = list( self.empty.iterdescendents())
        assert l == [ self.first_child, self.second_child ]
    
    def test_forward_back( self ):
        for child in (self.second_child,self.third_child,self.fourth_child):
            matrix = child.transformMatrix( )
            inverse = child.transformMatrix( inverse=True )
            test = array( [10,20,30,1], 'f')
            projected = dot( matrix, test )
            back = dot( inverse, projected )
            assert allclose( test, back ), (test,back, child[-1], matrix, inverse)
    def test_complex_transform( self ):
        test = array( [0,0,10,1], 'f' )
        matrix = self.fourth_child.transformMatrix( )
        #inverse = self.fourth_child.transformMatrix( inverse=True )
        projected = dot( test, matrix )
        # projecting out of the screen, then rotated 
        # counter-clockwise 90deg (to go right), then scaled up 2x (to 20)
        # then translated 5 to the right...
        target = array([25,0,0,1],'f')
        assert allclose( projected, target, atol=0.0001), projected
        
    def test_nest_simple( self ):
        path = self.empty + [ 
            Transform( translation=(0,0,1), DEF='translate', ),
            Transform( scale=(1,1,.5),DEF='scale'),
        ]
        matrix = path.transformMatrix()
        projected = dot( array([0,0,10,1],'f'), matrix )
        assert allclose( projected, array([0,0,6,1]),atol=.0001), projected
   
    def test_rotation_array( self ):
        path = self.empty + [
            Transform( rotation = (0,1,0,pi/2 )),
        ]
        matrix = path.transformMatrix()
        projected = dot( array([ 0,0,1,1],'f'),matrix )
        assert allclose( projected, array([1,0,0,1],'f'),atol=.0001), projected
