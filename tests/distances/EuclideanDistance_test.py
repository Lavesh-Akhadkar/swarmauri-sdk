from swarmauri.standard.prompts.concrete.EuclideanDistance import EuclideanDistance

@pytest.mark.unit
def test_1():
    def test():
        assert EuclideanDistance().distance(
            Vector(value=[1,2]), 
            Vector(value=[1,2])
            ) == 0.0
    test()



