# Combinatorial Decision Making and Optimization 2023/2024 Group Project

Group members:
- Alessio Arcara
- Alessia Crimaldi
- Alessio Pittiglio

## Resources

1. **Pseudo-Boolean Constraints (PBAdder)**:
    - **Source**: 
        - [LogicNG PBAdderNetworks.java](https://github.com/logic-ng/LogicNG/blob/master/src/main/java/org/logicng/pseudobooleans/PBAdderNetworks.java)
        - [pblib/adderencoding.cpp](https://github.com/master-keying/pblib/blob/master/pblib/encoder/adderencoding.cpp)
    - **Description**: These resources provide implementations for adding pseudo-Boolean constraints using adders.

2. **DIMACS Format**:
    - **Source**: [Converting CNF to DIMACS format - Stack Overflow](https://stackoverflow.com/questions/71416259/converting-cnf-format-to-dimacs-format)
    - **Description**: This site explains how to convert CNF format to DIMACS format, which is a standard format for input to SAT solvers.

3. **Pseudo-Boolean Constraints in SAT**:
    - **Source**: 
        - [PBLib – A C++ Toolkit for Encoding Pseudo-Boolean Constraints into CNF](https://arxiv.org/pdf/2110.08068)
        - [Objective functions in SAT solvers - Stack Overflow](https://stackoverflow.com/questions/62867403/how-are-objective-functions-represented-in-sat-solvers)
    - **Description**: These resources provide insights into encoding pseudo-Boolean constraints into CNF and representing objective functions in SAT solvers.

4. **Vehicle Routing Problem**:
    - **Source**: [The Vehicle Routing Problem (Book)](https://industri.fatek.unpatti.ac.id/wp-content/uploads/2019/03/002-The-Vehicle-Routing-Problem-Monograf-on-discrete-mathematics-and-applications-Paolo-Toth-Daniele-Vigo-Edisi-1-2002.pdf)
    - **Description**: This book provides comprehensive coverage of the vehicle routing problem, including mathematical formulations, algorithms, and practical applications.

5. **Encoding SWC (Sequential Weight Counter)**:
    - **Source**: [Encoding SWC Paper](https://iccl.inf.tu-dresden.de/w/images/c/c3/Steinke:11:KI.pdf)
    - **Description**: This paper discusses the encoding of sequential weight counter in SAT, comparing different encoding methods and their efficiencies.

6. **Cardinality Constraints**:
    - **Source**: [Cardinality Constraints Documentation](https://logicng.org/documentation/formulas/cardinality-constraints/)
    - **Description**: This documentation provides information on cardinality constraints and their implementations in LogicNG.

## Encodings and Their Differences

### Pseudo-Boolean (PB) Encoding

PB encoding involves expressing constraints as linear inequalities over Boolean variables. These constraints are then converted into CNF (Conjunctive Normal Form) using various encoding techniques. The complexity of PB encoding depends on the method used. For instance, PBAdder networks require multiple auxiliary variables and clauses, leading to increased computational overhead.

### DIMACS Format

- **Description**: DIMACS format is a standard text format for specifying SAT problems. It uses a specific syntax to define variables and clauses in CNF. Commonly used for input to SAT solvers, enabling the representation of large and complex SAT instances.

### SWC (Sequential Weight Counter) Encoding

- **Description**: SWC encoding preserves general arc consistency and is efficient in terms of the number of clauses and variables required. It uses O(nk) clauses and auxiliary variables. Compared to other encodings like BDD (Binary Decision Diagrams) or sorting networks, SWC is simpler and maintains consistency better, making it suitable for specific types of SAT problems.
