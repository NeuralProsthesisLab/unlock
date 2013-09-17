#ifndef PROPERTY_H
#define PROPERTY_H

#include <string>

#include "Enobio3GAPI_global.h"

#define MAX_LEN_VALUE   50
#define MAX_LEN_NAME   50

/*!
 * \class Property Property.h
 *
 * \brief Class that encapsulates a property value
 *
 */
class ENOBIO3GAPISHARED_EXPORT Property
{
public:
    /*!
     * Constructor that initializes the property with a string value.
     *
     * \param name Name of the property.
     *
     * \param value Value of the property.
     */
    Property (const char * name, const char * value);

    /*!
     * Constructor that initializes the property with an integer value.
     *
     * \param name Name of the property.
     *
     * \param value Value of the property.
     */
    Property (const char *  name, int value);

    /*!
     * Constructor that initializes the property with a float value.
     *
     * \param name Name of the property.
     *
     * \param value Value of the property.
     */
    Property (const char *  name, float value);

    /*!
     * It sets the property value from a string value
     *
     * \param value The string value
     */
    void setValue (const char *  value);

    /*!
     * It sets the property value from an integer value
     *
     * \param value The integer value
     */
    void setValue (int value);

    /*!
     * It sets the property value from a float value
     *
     * \param value The float value
     */
    void setValue (float value);

    /*!
     * It returns the name of the property
     *
     * \return Name of the property
     */
    const char * getName () const;

    /*!
     * It returns the property value as a string
     *
     * \return property value in string format
     */
    const char * getValueAsString () const;

    /*!
     * It returns the property value as an integer
     *
     * \return property value in integer format
     */
    int getValueAsInteger () const;

    /*!
     * It returns the property value as a float
     *
     * \return property value in float format
     */
    float getValueAsFloat () const;

private:
    /*!
     * String where the property name is stored
     */
    char _name[MAX_LEN_NAME];
    /*!
     * Integer used to store he propery value in integer format.
     */
    int _iValue;
    /*!
     * Float used to store he propery value in float format.
     */
    float _fValue;
    /*!
     * String used to store he propery value in string format.
     */
    char _strValue[MAX_LEN_VALUE];

};

#endif // PROPERTY_H
