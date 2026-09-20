import { useState } from 'react'
import { ChevronDown, Globe } from 'lucide-react'

const LANGUAGES = [
  { code: 'en', label: 'English',  native: 'English'  },
  { code: 'hi', label: 'Hindi',    native: 'हिन्दी'   },
  { code: 'mr', label: 'Marathi',  native: 'मराठी'    },
]

/**
 * LanguageSelector — Dropdown to choose the assistant language.
 *
 * UI-only for now. Translation will be implemented in a future phase.
 *
 * @param {object}   props
 * @param {string}   props.value      - Currently selected language code ('en'|'hi'|'mr')
 * @param {function} props.onChange   - Callback receiving the new language code
 * @param {string}   props.className  - Additional Tailwind classes
 */
export default function LanguageSelector({ value = 'en', onChange, className = '' }) {
  const [open, setOpen] = useState(false)

  const selected = LANGUAGES.find((l) => l.code === value) || LANGUAGES[0]

  const handleSelect = (code) => {
    setOpen(false)
    if (onChange) onChange(code)
  }

  return (
    <div className={`relative ${className}`}>
      {/* Trigger */}
      <button
        id="language-selector-trigger"
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="
          flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium
          bg-white border border-[#E5E7EB] text-[#1F2937]
          hover:border-[#8B5CF6] hover:text-[#6D28D9] hover:bg-[#F3E8FF]
          transition-colors duration-150 select-none
        "
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <Globe size={15} className="text-[#6D28D9]" />
        <span>{selected.native}</span>
        <ChevronDown
          size={14}
          className={`text-[#6B7280] transition-transform duration-150 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {/* Dropdown */}
      {open && (
        <>
          {/* Backdrop to close on outside click */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <ul
            role="listbox"
            className="
              absolute right-0 z-20 mt-1 w-36
              bg-white border border-[#E5E7EB] rounded-lg shadow-soft
              py-1 overflow-hidden
            "
          >
            {LANGUAGES.map((lang) => (
              <li
                key={lang.code}
                role="option"
                aria-selected={lang.code === value}
                onClick={() => handleSelect(lang.code)}
                className={`
                  flex items-center gap-2 px-3 py-2 text-sm cursor-pointer
                  transition-colors duration-100
                  ${lang.code === value
                    ? 'bg-[#F3E8FF] text-[#6D28D9] font-medium'
                    : 'text-[#1F2937] hover:bg-gray-50'
                  }
                `}
              >
                <span>{lang.native}</span>
                {lang.code !== lang.label.toLowerCase() && (
                  <span className="text-[#6B7280] text-xs">{lang.label}</span>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
