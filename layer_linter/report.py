class Report:
    def __init__(self):
        self.kept_contracts = []
        self.broken_contracts = []
        self.has_broken_contracts = False

    def add_contract(self, contract):
        if contract.is_kept:
            self.kept_contracts.append(contract)
        else:
            self.broken_contracts.append(contract)
            self.has_broken_contracts = True

    def output(self):
        if not (self.kept_contracts or self.broken_contracts):
            print('No contracts found.')

        # Print summary line.
        print('Contracts: {} kept, {} broken.'.format(
            len(self.kept_contracts),
            len(self.broken_contracts)
        ))
        for broken_contract in self.broken_contracts:
            print('- Broken contract {}:'.format(broken_contract.name))
            for illegal_dependency in broken_contract.illegal_dependencies:

                # Include information of the modules involved in an indirect import.
                indirect_info = ''
                if len(illegal_dependency) > 2:
                    indirect_info = ' (via {})'.format(
                        ', '.join(illegal_dependency[1:-1])
                    )

                print(
                    '  - {upstream_module} not allowed to import '
                    '{downstream_module}{indirect_info}.'.format(
                        upstream_module=illegal_dependency[0],
                        downstream_module=illegal_dependency[-1],
                        indirect_info=indirect_info,
                    )
                )
