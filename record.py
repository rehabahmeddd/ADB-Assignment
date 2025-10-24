
from dataclasses import dataclass

FIELD_SIZES = {
    "NAME": 30,
    "SSN": 9,
    "DEPARTMENTCODE": 9,
    "ADDRESS": 40,
    "PHONE": 9,
    "BIRTHDATE": 8,
    "SEX": 1,
    "JOBCODE": 4,
    "SALARY": 4,
}
DELETION_MARKER_SIZE = 1
RECORD_SIZE = sum(FIELD_SIZES.values()) + DELETION_MARKER_SIZE

@dataclass
class Record:
    name: str
    ssn: str
    departmentcode: str
    address: str
    phone: str
    birthdate: str
    sex: str
    jobcode: str
    salary: str
    deleted: bool = False

    def pack(self) -> bytes:
        parts = []
        for field_name, size in FIELD_SIZES.items():
            value = getattr(self, field_name.lower())
            bs = str(value).encode('utf-8')[:size]
            if len(bs) < size:
                bs += b' ' * (size - len(bs))
            parts.append(bs)
        parts.append(b'1' if self.deleted else b'0')
        return b''.join(parts)

    @classmethod
    def unpack(cls, data: bytes) -> 'Record':
        pos = 0
        kwargs = {}
        for field_name, size in FIELD_SIZES.items():
            raw = data[pos:pos+size]
            kwargs[field_name.lower()] = raw.decode('utf-8').rstrip(' ')
            pos += size
        del_mark = data[pos:pos+DELETION_MARKER_SIZE]
        kwargs['deleted'] = (del_mark == b'1')
        return cls(**kwargs)

    def __repr__(self):
        return f"Record(SSN={self.ssn}, NAME={self.name}, deleted={self.deleted})"


