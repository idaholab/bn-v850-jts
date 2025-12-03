# V850 Jump Table Resolver Plugin for Binary Ninja
A Binary Ninja architecture plugin to help resolve V850 jump tables.

## Overview
This plugin provides a solution for discovering and resolving jump tables for the V850 architecture. It is complimented
by the [V850 Architecture Plugin](https://github.com/idaholab/bn-v850-arch)

## Installation
1. Download/clone the latest source into your Binary Ninja plugin directory
    ```bash
    git clone https://github.com/idaholab/bn-v850-jts.git $HOME/.binaryninja/plugins/
    ```
2. Restart Binary Ninja

## Usage
1. Open a V850 file in Binary Ninja
2. Once the file has been analyzed, select Plugins -> Fix V850 jump tables
3. Wait for the jump tables to be resolved

> In order to resolve all jump tables, you may need to run multiple cycles of this plugin -> linear sweep -> reanalyze
> until no more new functions are added.

## Contributing
Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Resources
- [Binary Ninja API Documentation](https://api.binary.ninja/)
- [V850E1 Architecture Instruction Set Reference](https://www.renesas.com/en/document/mah/v850-familytm-architecture)

## License
Licensed under MIT.

See [LICENSE](LICENSE) file for details.

## Credits
Please see the [NOTICE](NOTICE.txt) file for details.

## Support
If you encounter issues with this repository, please create an [issue](https://github.com/idaholab/bn-st10-arch/issues).
