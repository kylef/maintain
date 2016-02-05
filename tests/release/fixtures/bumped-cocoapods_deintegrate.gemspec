Gem::Specification.new do |spec|
  spec.name          = 'cocoapods-deintegrate'
  spec.version       = '1.1.0'
  spec.authors       = ['Kyle Fuller']
  spec.email         = ['kyle@fuller.li']
  spec.summary       = 'A CocoaPods plugin to remove and de-integrate CocoaPods from your project.'
  spec.homepage      = 'https://github.com/kylef/cocoapods-deintegrate'
  spec.license       = 'MIT'

  spec.files         = Dir['lib/**/*.rb'] + %w( README.md LICENSE )
  spec.require_paths = ['lib']

  spec.required_ruby_version = '>= 2.0.0'
end
