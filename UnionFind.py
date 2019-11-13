class UnionFind():

    def __init__(self, num_elements):
        self.num_sets = num_elements
        self.up = []
        self.weight = []
        self.height = []
        for i in range (num_elements):
            self.up.append(-1)
            self.weight.append(1)
            self.height.append(0)

    def find_leader(self, element):
        """
        Find the leader of a given element and apply path compression
        :param element: The element to search
        :return: the leader
        """
        prev = element
        counter = 0
        #print(element)
        while self.up[element] != -1:
            element = self.up[element]
            counter += 1

        for i in range(counter):
            temp = self.up[prev]
            self.up[prev] = element
            prev = temp

        return element

    def get_size(self, element):
        """
        Get the size of the set that has element in it
        :param element: the element to search
        :return: weight of the set
        """
        return self.weight[self.find_leader(element)]

    def get_height(self, element):
        """
        Get the height of the set that has element in it
        :param element: the element to search
        :return: height of the set
        """
        return self.height[self.find_leader(element)]

    def union(self, element1, element2):
        """
        Performs a union of 2 sets by making the leader of the smaller set a child of the leader of the bigger set
        :param element1: element of the 1st set
        :param element2: element of the 2nd set
        :return: void
        """
        leader1 = self.find_leader(element1)
        leader2 = self.find_leader(element2)
        if leader1 == leader2:
            return
        if self.weight[leader1] >= self.weight[leader2]:
            self.up[leader2] = leader1
            self.weight[leader1] += self.weight[leader2]
            if self.height[leader2] >= self.height[leader1]:
                self.height[leader1] = self.height[leader2] + 1
        else:
            self.up[leader1] = leader2
            self.weight[leader2] += self.weight[leader1]
            if self.height[leader1] >= self.height[leader2]:
                self.height[leader2] = self.height[leader1] + 1
        self.num_sets -= 1

    def get_num_sets(self):
        """
        Get the current number of sets
        :return: Number of sets
        """
        return self.num_sets
