import sys
import unittest
import os
import tempfile
from numarray import *
import chararray
from tables import *
from numarray import typeDict

from test_all import verbose

class BasicTestCase(unittest.TestCase):
    """Basic test for all the supported typecodes present in Numeric.
    All of them are included on pytables.
    """
    endiancheck = 0

    def setUp(self):
        # Create an instance of HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, mode = "w")
        self.root = self.fileh.root

    def tearDown(self):
        # Close the file (eventually destroy the extended type)
        self.fileh.close()

        # Then, delete the file
        os.remove(self.file)

    def WriteRead(self, testArray):
        if verbose:
            print '\n', '-=' * 30
	    print "Running test for array with typecode '%s'" % \
	          testArray.__class__.__name__

	# Create the array under root and name 'somearray'
	a = testArray
        if self.endiancheck and not (isinstance(a, chararray.CharArray)):
            a.byteswap()
            pass
        #self.root.somearray = createArray(a, "Some array")
        self.fileh.createArray(self.root, 'somearray', a, "Some array")
	
        # Close the file
        self.fileh.close()
	
	# Re-open the file in read-only mode
        self.fileh = openFile(self.file, mode = "r")
        self.root = self.fileh.root
	
	# Read the saved array
	b = self.root.somearray.read()
	
	# Compare them. They should be equal.
	if a.tolist() <> b.tolist() and verbose:
	    print "Write and read arrays differ!"
	    print "Array written:", a
	    print "Array written shape:", a.shape
	    print "Array written itemsize:", a.itemsize()
	    print "Array written type:", a.type()
	    print "Array read:", b
	    print "Array read shape:", b.shape
	    print "Array read itemsize:", b.itemsize()
	    print "Array read type:", b.type()

        # Check the array equality as follows, not as in:
        # assert a == b
        # because the result is not what we want.
        assert a.shape == b.shape
        assert a.shape == self.root.somearray.shape
        if (isinstance(a, chararray.CharArray)):
            assert str(self.root.somearray.typeclass) == "CharType"
        else:
            assert a.type() == b.type()
            assert a.type() == self.root.somearray.typeclass
            assert a._byteorder == b._byteorder
            assert a._byteorder == self.root.somearray.byteorder
	assert a.tolist() == b.tolist()
	return
    
    def test00_char(self):
        "Checking a character array"
        
	a = chararray.array(self.tupleChar)
	self.WriteRead(a)
	return

    def test01_unsignedByte(self):
        "Checking a unsigned byte array"
        
	a = array(self.tupleInt, UInt8)
	self.WriteRead(a)
	return
    
    def test02_signedByte(self):
        "Checking a signed byte array"
        
	a = array(self.tupleInt, Int8)
	self.WriteRead(a)
	return
    
    def test03_signedShort(self):
        "Checking a signed short integer array"
                
	a = array( self.tupleInt, Int16)
	self.WriteRead(a)
	return
        
    def test04_unsignedShort(self):
        "Checking an unsigned short integer array"
                
	a = array( self.tupleInt, UInt16)
	self.WriteRead(a)
	return
        
    def test05_signedInt(self):
        "Checking a signed integer array"

	a = array( self.tupleInt, Int32)
	self.WriteRead(a)
	return
    
    def test06_unsignedInt(self):
        "Checking an unsigned integer array"

	a = array( self.tupleInt, UInt32)
	self.WriteRead(a)
	return
    
    def test07_LongLong(self):
        "Checking a signed long integer array"

	a = array( self.tupleInt, Int64)
	self.WriteRead(a)
	return
    
    def test07b_unsignedLongLong(self):
        "Checking a unsigned long integer array"

	a = array( self.tupleInt, UInt64)
	self.WriteRead(a)
	return
    
    def test08_float(self):
        "Checking a single precision floating point array"

	a = array( self.tupleInt, Float32)
	self.WriteRead(a)
	return
    
    def test09_double(self):
        "Checking a double precision floating point array"

	a = array( self.tupleInt, Float64)
	self.WriteRead(a)
	return

    def test10_complexSimple(self):
        "Checking a complex floating point array (not supported)"

	a = array( self.tupleInt, Complex32)
        try:
            self.WriteRead(a)
        except TypeError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next TypeError was catched!"
                print value
        else:
            self.fail("expected an TypeError")
            
    def test11_complexDouble(self):
        "Checking a complex floating point array (not supported)"

	a = array( self.tupleInt, Complex64)
        try:
            self.WriteRead(a)
        except TypeError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next TypeError was catched!"
                print value
        else:
            self.fail("expected an TypeError")

class BasicScalarTestCase(BasicTestCase):
    # Scalar case
    tupleInt = 3
    tupleChar = "3"
    
class Basic1DTestCase(BasicTestCase):
    # 1D case
    tupleInt = (3, 4, 5)
    tupleChar = ("aaa", "bbb", "ccc")
    endiancheck = 1
    
class Basic2DTestCase(BasicTestCase):
    # 2D case
    tupleInt = array(arange((4)**2), shape=(4,)*2) 
    tupleChar = chararray.array("abc"*3**2, shape=(3,)*2, itemsize=3)
    endiancheck = 1
    
class Basic10DTestCase(BasicTestCase):
    # 10D case
    tupleInt = array(arange((2)**10), shape=(2,)*10)
    # Chararray seems to cause some problems with somewhat large dimensions
    # Reverting to 2D case
    #tupleChar = chararray.array("abc"*2**10, shape=(2,)*10, itemsize=3)
    tupleChar = chararray.array("abc"*3**3, shape=(3,)*3, itemsize=3)
    
class Basic32DTestCase(BasicTestCase):
    # 32D case (maximum)
    tupleInt = array((32,), shape=(1,)*32) 
    # Chararray seems to cause some problems with somewhat large dimensions
    # Reverting to 2D case
    #tupleChar = chararray.array("121", shape=(1,)*32, itemsize=3)
    tupleChar = chararray.array("121"*3**2, shape=(3,)*2, itemsize=3)
    
class GroupsArrayTestCase(unittest.TestCase):
    """This test class checks combinations of arrays with groups.
    It also uses arrays ranks which ranges until 10.
    """

    def test00_iterativeGroups(self):
	
	"""Checking combinations of arrays with groups
	It also uses arrays ranks which ranges until 10.
	"""
	
	if verbose:
            print '\n', '-=' * 30
            print "Running %s.test00_iterativeGroups..." % \
	          self.__class__.__name__
		  
	# Open a new empty HDF5 file
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, mode = "w")
	
	# Get the root group
	group = fileh.root
	
	# Set the type codes to test
	#typecodes = ["c", 'b', '1', 's', 'w', 'i', 'u', 'l', 'f', 'd']
	typecodes = [Int8, UInt8, Int16, UInt16, Int32, UInt32, Int64, UInt64,
                     Float32, Float64]
	i = 1
	for typecode in typecodes:
	    # Create an array of typecode, with incrementally bigger ranges
	    a = ones((3,) * i, typecode)
	    # Save it on the HDF5 file
	    dsetname = 'array_' + `typecode`
	    if verbose:
		print "Creating dataset:", group._f_join(dsetname)
	    hdfarray = fileh.createArray(group, dsetname, a, "Large array")
	    # Create a new group
	    group = fileh.createGroup(group, 'group' + str(i))
	    # increment the range for next iteration
	    i += 1

	# Close the file
	fileh.close()

	# Open the previous HDF5 file in read-only mode
        fileh = openFile(file, mode = "r")
	# Get the root group
	group = fileh.root

	# Get the metadata on the previosly saved arrays
	for i in range(1,len(typecodes)):
	    # Create an array for later comparison
	    a = ones((3,) * i, typecodes[i - 1])
	    # Get the dset object hanging from group
	    dset = getattr(group, 'array_' + `typecodes[i-1]`)
	    # Get the actual array
	    b = dset.read()
	    if verbose:
		print "Info from dataset:", dset._v_pathname
		print "  Shape: ==>", dset.shape, 
		print "  typeclass ==> %s" % dset.typeclass
		print "Array b read from file. Shape: ==>", b.shape,
		print ". Type ==>" % b.type()
	    assert a.shape == b.shape
            assert a.type() == b.type()
            assert a.tolist() == b.tolist()
	    # Iterate over the next group
	    group = getattr(group, 'group' + str(i))

	# Close the file
	fileh.close()

	# Then, delete the file
        os.remove(file)

    def test01_largeRankArrays(self):
	"""Checking creation of large rank arrays (0 < rank <= 32)
	It also uses arrays ranks which ranges until maxrank.
	"""
	
	# maximum level of recursivity (deepest group level) achieved:
	# maxrank = 32 (for a effective maximum rank of 32)
        # This limit is due to HDF5 library limitations.
	# There seems to exist a bug in Numeric when dealing with
	# arrays with rank greater than 20. Also hdf5Extension has a
	# bug getting the shape of the object, that creates lots of
	# problems (segmentation faults, memory faults...)
	minrank = 1
	maxrank = 32
	
	if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_largeRankArrays..." % \
	          self.__class__.__name__
	    print "Maximum rank for tested arrays:", maxrank
	# Open a new empty HDF5 file
        #file = tempfile.mktemp(".h5")
        file = "test_array.h5"
        fileh = openFile(file, mode = "w")
	group = fileh.root
	if verbose:
	    print "Rank array writing progress: ",
	for rank in range(minrank, maxrank + 1):
	    # Create an array of integers, with incrementally bigger ranges
	    a = ones((1,) * rank, 'i')
	    if verbose:
		print "%3d," % (rank),
	    fileh.createArray(group, "array", a, "Rank: %s" % rank)
	    group = fileh.createGroup(group, 'group' + str(rank))
        # Flush the buffers
        fileh.flush()
	# Close the file
	fileh.close()
        
	# Open the previous HDF5 file in read-only mode
        fileh = openFile(file, mode = "r")
	group = fileh.root
	if verbose:
	    print
	    print "Rank array reading progress: "
	# Get the metadata on the previosly saved arrays
        for rank in range(minrank, maxrank + 1):
	    # Create an array for later comparison
	    a = ones((1,) * rank, 'i')
	    # Get the actual array
	    b = group.array.read()
	    if verbose:
		print "%3d," % (rank),
	    if verbose and 0:
		print "Info from dataset:", dset._v_pathname
		print "  Shape: ==>", dset.shape, 
		print "  typecode ==> %c" % dset.typecode
		print "Array b read from file. Shape: ==>", b.shape,
		print ". Type ==> %c" % b.type()
                
            # ************** WARNING!!! *****************
            # If we compare to arrays of dimensions bigger than 20
            # we get a segmentation fault! It is most probably a bug
            # located on Numeric package
            # I've discovered that comparing shapes and using the
            # tolist() conversion is the best to compare Numeric
            # arrays!. At least, tolist() do not crash!.
            # In addition, a == b is comparing the arrays element to
            # element and in ranks are different, the smaller is
            # promoted to the bigger rank. This is definitely not what
            # we want to do!!
            # ************** WARNING!!! *****************
            assert a.shape == b.shape
            assert a.type() == b.type()
            assert a.tolist() == b.tolist()
            #print fileh
	    # Iterate over the next group
	    group = fileh.getNode(group, 'group' + str(rank))

        if verbose:
            print # This flush the stdout buffer
	# Close the file
	fileh.close()
	
	# Delete the file
        os.remove(file)
	
def suite():
    theSuite = unittest.TestSuite()

    # The scalar case test should be refined in order to work
    # theSuite.addTest(unittest.makeSuite(BasicScalarTestCase))
    theSuite.addTest(unittest.makeSuite(Basic1DTestCase))
    theSuite.addTest(unittest.makeSuite(Basic2DTestCase))
    theSuite.addTest(unittest.makeSuite(Basic10DTestCase))
    theSuite.addTest(unittest.makeSuite(Basic32DTestCase))
    theSuite.addTest(unittest.makeSuite(GroupsArrayTestCase))

    return theSuite


if __name__ == '__main__':
    unittest.main( defaultTest='suite' )