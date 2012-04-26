

class Country(object):
    
    def __init__(self, id, name, phone_international_prefix,
                 phone_landline_zero_prefix, phone_landline_patterns,
                 phone_mobile_patterns):
        if id == None:
            raise NameError('id cannot be null.')
        if name == None:
            raise NameError('name cannot be null.')
        if phone_international_prefix == None:
            raise NameError('phone-international-prefix cannot be null.')
        if phone_landline_patterns == None:
            raise NameError('phone-landline-patterns cannot be null.')
        if phone_mobile_patterns == None:
            phone_mobile_patterns = []
        self.id = id
        self.name = name
        self.phone_international_prefix = phone_international_prefix
        self.phone_landline_zero_prefix = phone_landline_zero_prefix
        self.phone_landline_patterns = phone_landline_patterns
        self.phone_mobile_patterns = phone_mobile_patterns
        
        import re
        re_clean_prefix = re.compile('(^[^0-9]*0+)|([^0-9]+)')
        re_clean_prefix_pattern = re.compile('[^0-9xo]+')
        re_clean_prefix_pattern_zero = re.compile('(^[^0-9xo]*0+)|([^0-9xo]+)')
        re_extract_prefix_pattern = re.compile('^(\d*)(x+)(o*)$')
        
        self.phone_international_prefix = "00" + re_clean_prefix.sub('', self.phone_international_prefix)
        
        if self.phone_landline_zero_prefix:
            self.phone_landline_patterns = [re_clean_prefix_pattern.sub('', x) for x in self.phone_landline_patterns]
        else:
            self.phone_landline_patterns = [re_clean_prefix_pattern_zero.sub('', x) for x in self.phone_landline_patterns]
        self.phone_mobile_patterns = [re_clean_prefix_pattern_zero.sub('', x) for x in self.phone_mobile_patterns]
        
        all = []
        patterns = []
        for pattern in self.phone_landline_patterns:
            match = re_extract_prefix_pattern.match(pattern);
            all.append('%s%s' % (self.phone_international_prefix, match.group(1)))
            patterns.append(re.compile('^%s%s[0-9]{%s}[0-9]{0,%s}$' % (self.phone_international_prefix, match.group(1), len(match.group(2)), len(match.group(3)))))
        self.phone_landline_patterns = patterns
        patterns = []
        for pattern in self.phone_mobile_patterns:
            match = re_extract_prefix_pattern.match(pattern);
            all.append('%s%s' % (self.phone_international_prefix, match.group(1)))
            patterns.append(re.compile('^%s%s[0-9]{%s}[0-9]{0,%s}$' % (self.phone_international_prefix, match.group(1), len(match.group(2)), len(match.group(3)))))
        self.phone_mobile_patterns = patterns
        
        self.phone_prefixes = all
    
    def is_valid_phone(self, phone):
    	return self.is_valid_landline_phone(phone) or self.is_valid_mobile_phone(phone)
        
    def is_valid_landline_phone(self, phone):
        for re in self.phone_landline_patterns:
            if re.match(phone):
                return True
        return False
    
    def is_valid_mobile_phone(self, phone):
        for re in self.phone_mobile_patterns:
            if re.match(phone):
                return True
        return False

    def is_valid_fax_phone(self, phone):
        for re in self.phone_landline_patterns:
            if re.match(phone):
                return True
        return False

class Countries(object):
    
    def __init__(self, context):
        self.context = context
        self.countries = {}
        self.countries_by_phone_prefix = {}
        self.countries_by_phone_prefix_sorted = []
        self.__load()
    
    def __load(self):
        import re
        import codecs
        file = codecs.open( self.context.options.countries_file, "r", "utf-8" )
        text = file.read()
        file.close()
        re_spaces = re.compile('\s+')
        re_enters = re.compile('[\r\n]+')
        re_comments = re.compile('/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/')
        re_countries = re.compile('([A-Za-z0-9]+)[\x20\t]*{([^}]*)}')
        re_properties = re.compile('([A-Za-z0-9\-]+)[\x20\t]*:([^;]*);')
        text = re_enters.sub(' ', re_comments.sub(' ', text))
        for m_category in re_countries.finditer(text):
            c_id = m_category.group(1)
            c_name = None
            c_phone_international_prefix = None;
            c_phone_landline_zero_prefix = False;
            c_phone_landline_patterns = None;
            c_phone_mobile_patterns = None;
            for m_property in re_properties.finditer(m_category.group(2)):
                p_name = m_property.group(1).strip().lower()
                p_value = m_property.group(2).strip()
                if p_name == 'name':
                    c_name = p_value
                elif p_name == 'phone-international-prefix':
                    c_phone_international_prefix = p_value
                elif p_name == 'phone-landline-zero-prefix':
                    c_phone_landline_zero_prefix = p_value.lower() == 'true'
                elif p_name == 'phone-landline-patterns':
                    c_phone_landline_patterns = p_value.lower().split(',')
                elif p_name == 'phone-mobile-patterns':
                    c_phone_mobile_patterns = p_value.lower().split(',')
                else:
                    raise NameError('Unknown \'%s\' property.' % p_name)
            test = re_spaces.sub('', re_properties.sub('', m_category.group(2)))
            if len(test) > 0:
                raise NameError('Countries error: %s' % test)
            country = Country(c_id, c_name, c_phone_international_prefix, c_phone_landline_zero_prefix, c_phone_landline_patterns, c_phone_mobile_patterns)
            self.countries[country.id] = country
            for prefix in country.phone_prefixes:
                x = 0
                for prefix1 in self.countries_by_phone_prefix_sorted:
                    if (len(prefix) > len(prefix1) or (len(prefix) == len(prefix1) and prefix > prefix1)):
                        break
                    x += 1
                self.countries_by_phone_prefix[prefix] = country;
                self.countries_by_phone_prefix_sorted.insert(x, prefix);
        test = re_spaces.sub('', re_countries.sub('', text))
        if len(test) > 0:
            raise NameError('Countries error: %s' % test)
    
    def __getitem__(self, value):
        return self.countries[value]
    
    def get_by_phone(self, phone):
        for prefix in self.countries_by_phone_prefix_sorted:
            if phone.startswith(prefix):
                return self.countries_by_phone_prefix[prefix];
        return None
